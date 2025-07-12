# -*- coding: utf-8 -*-
{
    'name': 'POS Sales',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Sales order management for multi-tenant POS',
    'description': """
        POS Sales Module
        ==============
        
        This module provides sales order management for the multi-tenant POS system:
        
        * Shop-specific sales orders
        * Order line management
        * Payment processing
        * Sales reporting
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['pos_shop_core', 'pos_products', 'account'],
    'data': [
        'security/sales_security.xml',
        'security/ir.model.access.csv',
        'views/pos_order_views.xml',
        'views/pos_payment_views.xml',
        'views/menu_views.xml',
        'report/pos_order_report_views.xml',
        'report/pos_order_templates.xml',
    ],
    'demo': [
        # 'demo/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}