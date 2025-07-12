# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # Shop relationships
    shop_ids = fields.Many2many('pos.shop', 'shop_user_rel', 'user_id', 'shop_id', string='Assigned Shops')
    owned_shop_ids = fields.One2many('pos.shop', 'owner_id', string='Owned Shops')
    managed_shop_ids = fields.Many2many('pos.shop', 'shop_manager_rel', 'user_id', 'shop_id', string='Managed Shops')
    cashier_shop_ids = fields.Many2many('pos.shop', 'shop_cashier_rel', 'user_id', 'shop_id', string='Cashier Shops')
    pos_active_shop_id = fields.Many2one('pos.shop', string='Active Shop')
    
    # User role in POS system
    pos_role = fields.Selection([
        ('owner', 'Shop Owner'),
        ('manager', 'Shop Manager'),
        ('cashier', 'Cashier'),
    ], string='POS Role')
    
    # API Authentication fields
    api_token = fields.Char('API Token', copy=False, readonly=True)
    api_token_expiry = fields.Datetime('API Token Expiry', copy=False, readonly=True)
    
    @api.depends('owned_shop_ids', 'managed_shop_ids', 'cashier_shop_ids')
    def _compute_shop_ids(self):
        for user in self:
            shops = user.owned_shop_ids | user.managed_shop_ids | user.cashier_shop_ids
            user.shop_ids = shops
            
    @api.model
    def _check_token_validity(self):
        """Cron job to invalidate expired tokens"""
        expired_users = self.sudo().search([('api_token_expiry', '!=', False), ('api_token_expiry', '<', fields.Datetime.now())])
        if expired_users:
            expired_users.write({
                'api_token': False,
                'api_token_expiry': False
            })
            return True
        return False