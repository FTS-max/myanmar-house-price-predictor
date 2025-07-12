# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class PosSession(models.Model):
    _name = 'pos.session'
    _description = 'POS Session'
    _order = 'id desc'
    
    name = fields.Char(string='Session ID', required=True, readonly=True, default='/')
    user_id = fields.Many2one('res.users', string='Responsible', required=True, 
                             default=lambda self: self.env.user.id)
    shop_id = fields.Many2one('pos.shop', string='Shop', required=True)
    company_id = fields.Many2one('res.company', related='shop_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='shop_id.currency_id', readonly=True)
    
    # Session timing
    start_at = fields.Datetime(string='Opening Date', readonly=True)
    stop_at = fields.Datetime(string='Closing Date', readonly=True)
    
    # Session state
    state = fields.Selection([
        ('draft', 'New'),
        ('opened', 'In Progress'),
        ('closing_control', 'Closing Control'),
        ('closed', 'Closed & Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, default='draft')
    
    # Cash control
    cash_control = fields.Boolean(string='Cash Control', 
                                 help="Check the amount of the cashbox at opening and closing")
    cash_register_id = fields.Many2one('account.bank.statement', string='Cash Register', readonly=True)
    cash_register_balance_start = fields.Monetary(string='Starting Balance', readonly=True)
    cash_register_balance_end_real = fields.Monetary(string='Ending Balance')
    cash_register_balance_end = fields.Monetary(string='Computed Balance', 
                                              compute='_compute_cash_balance', readonly=True)
    cash_register_difference = fields.Monetary(string='Difference', 
                                             compute='_compute_cash_difference', readonly=True)
    
    # Related records
    order_ids = fields.One2many('pos.order', 'session_id', string='Orders')
    order_count = fields.Integer(string='Orders Count', compute='_compute_order_count')
    total_payments_amount = fields.Monetary(string='Total Payments', compute='_compute_total_payments')
    payment_method_ids = fields.Many2many('pos.payment.method', string='Payment Methods',
                                       related='shop_id.payment_method_ids', readonly=True)
    
    # Notes
    note = fields.Text(string='Internal Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('pos.session')
        return super(PosSession, self).create(vals_list)
    
    @api.depends('order_ids.payment_ids.amount')
    def _compute_total_payments(self):
        for session in self:
            session.total_payments_amount = sum(payment.amount for payment in 
                                             session.mapped('order_ids.payment_ids') 
                                             if payment.payment_status == 'done')
    
    @api.depends('order_ids')
    def _compute_order_count(self):
        for session in self:
            session.order_count = len(session.order_ids)
    
    @api.depends('cash_register_id.balance_end', 
                'cash_register_id.line_ids', 
                'cash_register_balance_start')
    def _compute_cash_balance(self):
        for session in self:
            if session.cash_register_id:
                session.cash_register_balance_end = session.cash_register_id.balance_end
            else:
                session.cash_register_balance_end = 0.0
    
    @api.depends('cash_register_balance_end', 'cash_register_balance_end_real')
    def _compute_cash_difference(self):
        for session in self:
            session.cash_register_difference = session.cash_register_balance_end_real - session.cash_register_balance_end
    
    @api.constrains('user_id', 'state')
    def _check_unicity(self):
        # Only one open session per user
        if self.search_count([('state', '=', 'opened'), 
                            ('user_id', '=', self.user_id.id), 
                            ('id', '!=', self.id)]):
            raise ValidationError(_('You cannot create two active sessions for the same user!'))
    
    @api.constrains('shop_id', 'state')
    def _check_shop_session(self):
        # Only one open session per shop if configured that way
        if self.shop_id.limit_sessions and self.search_count([('state', '=', 'opened'), 
                                                           ('shop_id', '=', self.shop_id.id), 
                                                           ('id', '!=', self.id)]):
            raise ValidationError(_('You cannot create multiple active sessions for this shop!'))
    
    def action_open_session(self):
        """Open the session"""
        for session in self:
            if session.state != 'draft':
                continue
                
            values = {
                'state': 'opened',
                'start_at': fields.Datetime.now()
            }
            
            if session.cash_control:
                # Create cash register (statement) for this session
                journal = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
                if not journal:
                    raise UserError(_('Please define a cash journal for this company.'))
                    
                statement = self.env['account.bank.statement'].create({
                    'journal_id': journal.id,
                    'date': fields.Date.context_today(self),
                    'name': session.name,
                    'balance_start': session.cash_register_balance_start,
                    'balance_end_real': session.cash_register_balance_start,
                })
                
                values.update({
                    'cash_register_id': statement.id,
                })
                
            session.write(values)
            
        return True
    
    def action_close_session(self):
        """Close the session"""
        for session in self:
            if session.state != 'opened':
                continue
                
            session.write({
                'state': 'closing_control',
                'stop_at': fields.Datetime.now(),
            })
            
        return True
    
    def action_validate_closing(self):
        """Post the session and mark it as closed"""
        for session in self:
            if session.state != 'closing_control':
                continue
                
            if session.cash_control and abs(session.cash_register_difference) > session.shop_id.cash_difference_threshold:
                return {
                    'name': _('Cash difference too high'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'pos.session',
                    'view_mode': 'form',
                    'res_id': session.id,
                    'target': 'new',
                    'context': {'cash_difference_warning': True},
                }
                
            # Close the cash register
            if session.cash_register_id:
                session.cash_register_id.balance_end_real = session.cash_register_balance_end_real
                session.cash_register_id.button_confirm_bank()
                
            # Mark all orders as done
            orders_to_finalize = session.order_ids.filtered(lambda order: order.state == 'paid')
            orders_to_finalize.write({'state': 'done'})
                
            session.write({'state': 'closed'})
            
        return True
    
    def action_cancel_session(self):
        """Cancel the session"""
        for session in self:
            if session.state not in ['draft', 'opened']:
                raise UserError(_('Cannot cancel a session that is already closed.'))
                
            # Cancel the cash register
            if session.cash_register_id:
                session.cash_register_id.button_cancel()
                
            # Cancel all draft orders
            orders_to_cancel = session.order_ids.filtered(lambda order: order.state == 'draft')
            orders_to_cancel.write({'state': 'cancel'})
                
            session.write({'state': 'cancelled'})
            
        return True