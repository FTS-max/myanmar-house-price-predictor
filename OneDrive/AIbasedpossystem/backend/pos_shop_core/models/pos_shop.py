# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PosShop(models.Model):
    _name = 'pos.shop'
    _description = 'POS Shop'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    name = fields.Char(string='Shop Name', required=True, tracking=True)
    code = fields.Char(string='Shop Code', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', readonly=True)
    
    # Shop owner and users
    owner_id = fields.Many2one('res.users', string='Shop Owner', required=True, tracking=True)
    manager_ids = fields.Many2many('res.users', 'shop_manager_rel', 'shop_id', 'user_id', string='Managers')
    cashier_ids = fields.Many2many('res.users', 'shop_cashier_rel', 'shop_id', 'user_id', string='Cashiers')
    
    # Shop details
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    website = fields.Char(string='Website')
    
    # Shop settings
    opening_time = fields.Float(string='Opening Time')
    closing_time = fields.Float(string='Closing Time')
    timezone = fields.Selection('_tz_get', string='Timezone')
    
    # Shop statistics (computed fields)
    product_count = fields.Integer(string='Products', compute='_compute_counts')
    order_count = fields.Integer(string='Orders', compute='_compute_counts')
    
    # API access
    api_key = fields.Char(string='API Key', copy=False, readonly=True, groups='base.group_system')
    
    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Shop code must be unique per company!')
    ]
    
    @api.model
    def _tz_get(self):
        return [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]
    
    @api.depends()
    def _compute_counts(self):
        for shop in self:
            shop.product_count = self.env['product.template'].search_count([('shop_id', '=', shop.id)])
            shop.order_count = self.env['pos.order'].search_count([('shop_id', '=', shop.id)])
    
    @api.model
    def create(self, vals):
        record = super(PosShop, self).create(vals)
        # Generate API key on creation
        if not record.api_key:
            record.sudo().api_key = self.env['ir.config_parameter'].sudo().get_param('database.uuid') + '-' + str(record.id)
        return record
    
    def generate_new_api_key(self):
        """Generate a new API key for the shop"""
        for shop in self:
            shop.sudo().api_key = self.env['ir.config_parameter'].sudo().get_param('database.uuid') + '-' + str(shop.id) + '-' + str(fields.Datetime.now().strftime('%Y%m%d%H%M%S'))
        return True
    
    def action_view_products(self):
        self.ensure_one()
        return {
            'name': _('Products'),
            'res_model': 'product.template',
            'view_mode': 'tree,form',
            'domain': [('shop_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_shop_id': self.id}
        }
    
    def action_view_orders(self):
        self.ensure_one()
        return {
            'name': _('Orders'),
            'res_model': 'pos.order',
            'view_mode': 'tree,form',
            'domain': [('shop_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_shop_id': self.id}
        }