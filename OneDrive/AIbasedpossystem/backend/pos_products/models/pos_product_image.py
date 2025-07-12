# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PosProductImage(models.Model):
    _name = 'pos.product.image'
    _description = 'Product Image for POS'
    _order = 'sequence'
    
    name = fields.Char(string='Name')
    sequence = fields.Integer(string='Sequence', default=10)
    image = fields.Binary(string='Image', attachment=True, required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='cascade', index=True)
    shop_id = fields.Many2one('pos.shop', string='Shop', related='product_tmpl_id.shop_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', related='shop_id.company_id', store=True, readonly=True)