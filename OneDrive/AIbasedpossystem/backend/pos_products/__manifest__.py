# -*- coding: utf-8 -*-
{
    'name': 'POS Products',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Product management for multi-tenant POS',
    'description': """
        POS Products Module
        ==============
        
        This module provides product management for the multi-tenant POS system:
        
        * Shop-specific products
        * Product categories
        * Inventory management
        * Pricing rules
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['pos_shop_core', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_product_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}