# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PosOrderLine(models.Model):
    _name = 'pos.order.line'
    _description = 'POS Order Line'
    _order = 'order_id, sequence'
    
    order_id = fields.Many2one('pos.order', string='Order', required=True, ondelete='cascade')
    name = fields.Char(string='Line Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Product information
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_template_id = fields.Many2one('product.template', related='product_id.product_tmpl_id')
    shop_id = fields.Many2one('pos.shop', related='order_id.shop_id', store=True, readonly=True)
    
    # Quantity and UoM
    qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id')
    
    # Pricing
    price_unit = fields.Float(string='Unit Price', digits='Product Price', required=True)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Float(string='Subtotal w/o Tax', compute='_compute_amount_line_all')
    price_subtotal_incl = fields.Float(string='Subtotal', compute='_compute_amount_line_all')
    
    # Additional information
    note = fields.Text(string='Note')
    
    @api.depends('price_unit', 'qty', 'discount', 'tax_ids')
    def _compute_amount_line_all(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(price, line.order_id.currency_id, line.qty, product=line.product_id)
            line.price_subtotal = taxes['total_excluded']
            line.price_subtotal_incl = taxes['total_included']
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        
        # Set name from product
        self.name = self.product_id.display_name
        
        # Get price from product
        if self.product_id.product_tmpl_id.list_price_shop:
            self.price_unit = self.product_id.product_tmpl_id.list_price_shop
        else:
            self.price_unit = self.product_id.lst_price
        
        # Check if there's a discount price
        product_tmpl = self.product_id.product_tmpl_id
        if product_tmpl.discount_price and product_tmpl.discount_start and product_tmpl.discount_end:
            now = fields.Datetime.now()
            if product_tmpl.discount_start <= now <= product_tmpl.discount_end:
                self.price_unit = product_tmpl.discount_price
        
        # Set taxes
        if self.order_id.shop_id:
            shop_settings = self.env['pos.shop.settings'].search([('shop_id', '=', self.order_id.shop_id.id)], limit=1)
            if shop_settings and shop_settings.default_tax_id:
                self.tax_ids = [(6, 0, [shop_settings.default_tax_id.id])]
            else:
                fpos = self.order_id.partner_id.property_account_position_id
                self.tax_ids = [(6, 0, fpos.map_tax(self.product_id.taxes_id).ids)] if fpos else [(6, 0, self.product_id.taxes_id.ids)]
    
    @api.constrains('product_id', 'shop_id')
    def _check_product_shop(self):
        for line in self:
            if line.product_id.product_tmpl_id.shop_id and line.product_id.product_tmpl_id.shop_id != line.shop_id:
                raise ValidationError(_('Product must belong to the same shop as the order.'))