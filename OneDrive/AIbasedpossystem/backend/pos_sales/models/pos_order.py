# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import json
import uuid

class PosOrder(models.Model):
    _name = 'pos.order'
    _description = 'POS Order'
    _order = 'date_order desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Order Ref', required=True, readonly=True, copy=False, default='/')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                               default=lambda self: self.env.company.id)
    date_order = fields.Datetime(string='Order Date', readonly=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Salesperson', required=True,
                            default=lambda self: self.env.user.id,
                            help="Person who created the order")
    
    # Amounts
    amount_total = fields.Float(string='Total', digits='Product Price', compute='_compute_amount_all')
    amount_tax = fields.Float(string='Taxes', digits='Product Price', compute='_compute_amount_all')
    amount_paid = fields.Float(string='Paid', digits='Product Price', compute='_compute_amount_paid')
    amount_return = fields.Float(string='Returned', digits='Product Price', compute='_compute_amount_paid')
    currency_id = fields.Many2one('res.currency', string='Currency', related='shop_id.currency_id')
    
    # Shop and session
    shop_id = fields.Many2one('pos.shop', string='Shop', required=True)
    session_id = fields.Many2one('pos.session', string='Session', required=True)
    
    # Order lines and payments
    lines = fields.One2many('pos.order.line', 'order_id', string='Order Lines')
    payment_ids = fields.One2many('pos.payment', 'order_id', string='Payments')
    
    # Customer information
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address')
    
    # Order state
    state = fields.Selection([
        ('draft', 'New'),
        ('paid', 'Paid'),
        ('done', 'Done'),
        ('invoiced', 'Invoiced'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, copy=False, default='draft', tracking=True)
    
    # Receipt information
    receipt_number = fields.Char(string='Receipt Number', readonly=True, copy=False)
    pos_reference = fields.Char(string='Receipt Ref', readonly=True, copy=False)
    
    # External identifiers
    external_id = fields.Char(string='External ID', copy=False, 
                            help="External identifier for API integration")
    
    # Additional information
    note = fields.Text(string='Internal Notes')
    
    # Accounting fields
    account_move_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    invoice_state = fields.Selection([
        ('no', 'Not Invoiced'),
        ('invoiced', 'Invoiced'),
    ], string='Invoice State', readonly=True, copy=False, default='no')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('pos.order')
            if not vals.get('external_id'):
                vals['external_id'] = str(uuid.uuid4())
            if not vals.get('receipt_number'):
                vals['receipt_number'] = self.env['ir.sequence'].next_by_code('pos.receipt')
            if not vals.get('pos_reference'):
                vals['pos_reference'] = vals.get('receipt_number')
        return super(PosOrder, self).create(vals_list)
    
    @api.depends('lines.price_subtotal_incl', 'lines.price_subtotal')
    def _compute_amount_all(self):
        for order in self:
            order.amount_tax = sum(line.price_subtotal_incl - line.price_subtotal for line in order.lines)
            order.amount_total = sum(line.price_subtotal_incl for line in order.lines)
    
    @api.depends('payment_ids.amount')
    def _compute_amount_paid(self):
        for order in self:
            payments = order.payment_ids.filtered(lambda p: p.payment_status == 'done')
            order.amount_paid = sum(payment.amount for payment in payments if not payment.is_change)
            order.amount_return = -sum(payment.amount for payment in payments if payment.is_change)
    
    @api.constrains('lines')
    def _check_lines(self):
        for order in self:
            if not order.lines:
                raise ValidationError(_('An order must have at least one line.'))
    
    @api.constrains('shop_id', 'company_id')
    def _check_shop_company(self):
        for order in self:
            if order.shop_id.company_id != order.company_id:
                raise ValidationError(_('Shop must belong to the same company as the order.'))
    
    def action_paid(self):
        """Mark the order as paid"""
        for order in self:
            if order.state != 'draft':
                continue
                
            # Check if the order is fully paid
            if order.amount_total > order.amount_paid:
                raise UserError(_('Cannot mark as paid: Order is not fully paid.'))
                
            order.write({'state': 'paid'})
        return True
    
    def action_done(self):
        """Mark the order as done"""
        for order in self:
            if order.state not in ['draft', 'paid']:
                continue
                
            # If not paid yet, mark as paid first
            if order.state == 'draft':
                order.action_paid()
                
            order.write({'state': 'done'})
        return True
    
    def action_cancel(self):
        """Cancel the order"""
        for order in self:
            if order.state in ['done', 'invoiced']:
                raise UserError(_('Cannot cancel a completed order.'))
                
            # Reverse payments if any
            for payment in order.payment_ids.filtered(lambda p: p.payment_status == 'done'):
                payment.reverse_payment()
                
            order.write({'state': 'cancel'})
        return True
    
    def action_create_invoice(self):
        """Create an invoice for this order"""
        for order in self:
            if order.state not in ['paid', 'done']:
                raise UserError(_('Cannot create invoice for unpaid order.'))
                
            if order.invoice_state == 'invoiced':
                raise UserError(_('This order is already invoiced.'))
                
            # Create invoice
            invoice_vals = order._prepare_invoice_vals()
            move = self.env['account.move'].create(invoice_vals)
            
            # Create invoice lines
            invoice_line_vals = []
            for line in order.lines:
                invoice_line_vals.append(order._prepare_invoice_line_vals(line, move))
            
            move.write({'invoice_line_ids': [(0, 0, line) for line in invoice_line_vals]})
            
            # Validate invoice
            move.action_post()
            
            # Update order
            order.write({
                'account_move_id': move.id,
                'invoice_state': 'invoiced',
                'state': 'invoiced'
            })
            
        return True
    
    def _prepare_invoice_vals(self):
        """Prepare values for invoice creation"""
        self.ensure_one()
        return {
            'partner_id': self.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.context_today(self),
            'invoice_origin': self.name,
            'currency_id': self.currency_id.id,
            'narration': self.note,
            'company_id': self.company_id.id,
            'invoice_user_id': self.user_id.id,
        }
    
    def _prepare_invoice_line_vals(self, line, move):
        """Prepare values for invoice line creation"""
        return {
            'product_id': line.product_id.id,
            'quantity': line.qty,
            'discount': line.discount,
            'price_unit': line.price_unit,
            'name': line.name,
            'tax_ids': [(6, 0, line.tax_ids.ids)],
            'product_uom_id': line.uom_id.id,
            'move_id': move.id,
        }
    
    def print_receipt(self):
        """Print the receipt"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/pos/receipt/%s' % self.id,
            'target': 'new',
        }
    
    def get_receipt_data(self):
        """Get data for receipt rendering"""
        self.ensure_one()
        
        # Format lines
        lines_data = []
        for line in self.lines:
            lines_data.append({
                'product_name': line.product_id.name,
                'quantity': line.qty,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'price_subtotal': line.price_subtotal,
                'price_subtotal_incl': line.price_subtotal_incl,
            })
        
        # Format payments
        payments_data = []
        for payment in self.payment_ids.filtered(lambda p: p.payment_status == 'done'):
            payments_data.append({
                'amount': payment.amount,
                'payment_method': payment.payment_method_id.name,
                'payment_date': payment.payment_date,
            })
        
        # Prepare receipt data
        receipt_data = {
            'order_name': self.name,
            'receipt_number': self.receipt_number,
            'date': self.date_order,
            'cashier': self.user_id.name,
            'shop': self.shop_id.name,
            'company': {
                'name': self.company_id.name,
                'phone': self.company_id.phone,
                'email': self.company_id.email,
                'website': self.company_id.website,
                'address': self.company_id.street + (', ' + self.company_id.city if self.company_id.city else ''),
            },
            'customer': self.partner_id.name if self.partner_id else None,
            'currency': self.currency_id.symbol,
            'lines': lines_data,
            'subtotal': sum(line.price_subtotal for line in self.lines),
            'tax': self.amount_tax,
            'total': self.amount_total,
            'payments': payments_data,
            'change': self.amount_return,
        }
        
        return receipt_data