# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PosPayment(models.Model):
    _name = 'pos.payment'
    _description = 'POS Payment'
    _order = 'id desc'
    
    name = fields.Char(string='Payment Reference', readonly=True, copy=False)
    order_id = fields.Many2one('pos.order', string='Order', required=True, ondelete='cascade')
    amount = fields.Float(string='Amount', required=True)
    payment_date = fields.Datetime(string='Payment Date', default=fields.Datetime.now, required=True)
    payment_method_id = fields.Many2one('pos.payment.method', string='Payment Method', required=True)
    
    # Related fields
    shop_id = fields.Many2one('pos.shop', related='order_id.shop_id', store=True, readonly=True)
    session_id = fields.Many2one('pos.session', related='order_id.session_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', readonly=True)
    
    # Transaction information
    transaction_id = fields.Char(string='Transaction ID', help="Payment provider's transaction ID")
    card_type = fields.Char(string='Card Type', help="Card type used for the payment (e.g. Visa, MasterCard)")
    cardholder_name = fields.Char(string='Cardholder Name')
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    ], string='Status', default='done', required=True)
    
    # Additional information
    note = fields.Text(string='Note')
    is_change = fields.Boolean(string='Is Change', default=False, 
                              help="True if this payment is used as change")
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('pos.payment')
        return super(PosPayment, self).create(vals_list)
    
    @api.constrains('amount')
    def _check_amount(self):
        for payment in self:
            if payment.amount <= 0 and not payment.is_change:
                raise ValidationError(_('Payment amount must be positive.'))
            if payment.amount >= 0 and payment.is_change:
                raise ValidationError(_('Change amount must be negative.'))
    
    def reverse_payment(self):
        """Reverse a payment"""
        for payment in self:
            if payment.payment_status != 'done':
                raise ValidationError(_('Only confirmed payments can be reversed.'))
            
            payment.write({
                'payment_status': 'reversed',
                'note': payment.note + '\n' + _('Payment reversed on %s') % fields.Datetime.now() if payment.note else _('Payment reversed on %s') % fields.Datetime.now()
            })
            
            # Create a new payment with negative amount to balance the books
            reversed_payment = payment.copy({
                'name': _('Reversal of %s') % payment.name,
                'amount': -payment.amount,
                'note': _('Reversal of payment %s') % payment.name,
                'payment_status': 'done',
                'payment_date': fields.Datetime.now(),
            })
            
            return reversed_payment