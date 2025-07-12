# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Shop relationship
    shop_id = fields.Many2one('pos.shop', string='Shop', index=True)
    shop_category_id = fields.Many2one('pos.product.category', string='Shop Category')
    
    # POS specific fields
    pos_available = fields.Boolean(string='Available in POS', default=True)
    pos_sequence = fields.Integer(string='POS Sequence', default=10)
    pos_description = fields.Text(string='POS Description')
    
    # Additional pricing
    list_price_shop = fields.Monetary(string='Shop Selling Price', currency_field='currency_id')
    discount_price = fields.Monetary(string='Discounted Price', currency_field='currency_id')
    discount_start = fields.Datetime(string='Discount Start')
    discount_end = fields.Datetime(string='Discount End')
    
    # Barcode and SKU
    shop_sku = fields.Char(string='Shop SKU')
    
    # Additional images
    pos_image_ids = fields.One2many('pos.product.image', 'product_tmpl_id', string='Additional Images')
    
    # Variants handling
    pos_use_variants = fields.Boolean(string='Use Variants in POS', default=True)
    
    # AI integration
    ai_description = fields.Text(string='AI Generated Description')
    ai_tags = fields.Char(string='AI Tags')
    
    _sql_constraints = [
        ('shop_sku_uniq', 'unique(shop_id, shop_sku)', 'Shop SKU must be unique per shop!')
    ]
    
    @api.onchange('shop_id')
    def _onchange_shop_id(self):
        if self.shop_id:
            self.company_id = self.shop_id.company_id
    
    @api.constrains('shop_id', 'company_id')
    def _check_shop_company(self):
        for product in self:
            if product.shop_id and product.company_id != product.shop_id.company_id:
                raise ValidationError(_('Product company must be the same as the shop company.'))
    
    def write(self, vals):
        # If shop_id is being changed, ensure company_id is updated accordingly
        if vals.get('shop_id'):
            shop = self.env['pos.shop'].browse(vals['shop_id'])
            vals['company_id'] = shop.company_id.id
        return super(ProductTemplate, self).write(vals)
    
    @api.model
    def create(self, vals):
        # If shop_id is provided, ensure company_id is set accordingly
        if vals.get('shop_id'):
            shop = self.env['pos.shop'].browse(vals['shop_id'])
            vals['company_id'] = shop.company_id.id
        return super(ProductTemplate, self).create(vals)
    
    def get_current_price(self):
        """Get the current price considering discounts"""
        self.ensure_one()
        now = fields.Datetime.now()
        if (self.discount_price and 
            self.discount_start and self.discount_end and 
            self.discount_start <= now <= self.discount_end):
            return self.discount_price
        return self.list_price_shop or self.list_price


class PosProductImage(models.Model):
    _name = 'pos.product.image'
    _description = 'POS Product Image'
    _order = 'sequence'
    
    name = fields.Char(string='Name')
    sequence = fields.Integer(string='Sequence', default=10)
    image = fields.Binary(string='Image', attachment=True, required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='cascade')