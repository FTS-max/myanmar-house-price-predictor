# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PosPaymentMethod(models.Model):
    _name = 'pos.payment.method'
    _description = 'POS Payment Method'
    _order = 'sequence, id'
    
    name = fields.Char(string='Payment Method', required=True, translate=True)
    code = fields.Char(string='Code', help="Technical code for API integration")
    sequence = fields.Integer(string='Sequence', default=10, help="Determines the display order")
    active = fields.Boolean(string='Active', default=True)
    
    # Shop relationship
    shop_id = fields.Many2one('pos.shop', string='Shop', 
                             help="If set, this payment method will only be available for this shop")
    company_id = fields.Many2one('res.company', string='Company', related='shop_id.company_id', store=True)
    
    # Payment method type
    is_cash_count = fields.Boolean(string='Cash', default=False, 
                                  help="If true, this payment method will be used for cash payments and will require cash counting")
    split_transactions = fields.Boolean(string='Split Transactions', default=False, 
                                       help="If true, each payment will generate a separate transaction")
    
    # Payment method configuration
    journal_id = fields.Many2one('account.journal', string='Journal', 
                               domain="[('type', 'in', ['bank', 'cash'])]",
                               help="Accounting journal used to post sales entries")
    receivable_account_id = fields.Many2one('account.account', string='Receivable Account', 
                                          domain="[('internal_type', '=', 'receivable')]",
                                          help="Account used for customer receivables")
    
    # UI/UX
    image = fields.Binary(string='Image', attachment=True, help="Image displayed for this payment method")
    description = fields.Text(string='Description', translate=True, 
                            help="Description displayed to the cashier when selecting this payment method")
    
    # API Integration
    use_payment_terminal = fields.Boolean(string='Use Payment Terminal', default=False)
    payment_terminal_provider = fields.Selection([
        ('none', 'None'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('square', 'Square'),
        ('custom', 'Custom Integration'),
    ], string='Payment Terminal Provider', default='none')
    terminal_api_key = fields.Char(string='API Key', groups='base.group_system',
                                 help="API Key for payment terminal integration")
    terminal_api_secret = fields.Char(string='API Secret', groups='base.group_system',
                                    help="API Secret for payment terminal integration")
    terminal_endpoint = fields.Char(string='API Endpoint', 
                                  help="API Endpoint for custom payment terminal integration")
    
    @api.onchange('is_cash_count')
    def _onchange_is_cash_count(self):
        if self.is_cash_count:
            self.split_transactions = False
            self.use_payment_terminal = False
            self.payment_terminal_provider = 'none'
    
    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal(self):
        if self.use_payment_terminal:
            self.is_cash_count = False
        else:
            self.payment_terminal_provider = 'none'
            self.terminal_api_key = False
            self.terminal_api_secret = False
            self.terminal_endpoint = False
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The payment method code must be unique!')
    ]