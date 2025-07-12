# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PosProductCategory(models.Model):
    _name = 'pos.product.category'
    _description = 'POS Product Category'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'sequence, name'
    
    name = fields.Char(string='Name', required=True, translate=True)
    complete_name = fields.Char(string='Complete Name', compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one('pos.product.category', string='Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('pos.product.category', 'parent_id', string='Child Categories')
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Shop relationship
    shop_id = fields.Many2one('pos.shop', string='Shop', required=True, index=True)
    company_id = fields.Many2one('res.company', related='shop_id.company_id', store=True, readonly=True)
    
    # Visual attributes
    image = fields.Binary(string='Image', attachment=True)
    color = fields.Integer(string='Color Index')
    
    # POS specific
    pos_available = fields.Boolean(string='Available in POS', default=True)
    pos_sequence = fields.Integer(string='POS Sequence', default=10)
    
    # Product count
    product_count = fields.Integer(string='Product Count', compute='_compute_product_count')
    
    _sql_constraints = [
        ('name_shop_uniq', 'unique(name, shop_id, parent_id)', 'Category name must be unique per shop and parent category!')
    ]
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name
    
    @api.depends()
    def _compute_product_count(self):
        for category in self:
            category.product_count = self.env['product.template'].search_count([('shop_category_id', '=', category.id)])
    
    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise models.ValidationError(_('Error! You cannot create recursive categories.'))
    
    @api.constrains('parent_id', 'shop_id')
    def _check_parent_shop(self):
        for category in self:
            if category.parent_id and category.parent_id.shop_id != category.shop_id:
                raise models.ValidationError(_('Parent category must belong to the same shop.'))