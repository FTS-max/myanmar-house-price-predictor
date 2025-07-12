{
    'name': 'POS Shop Core',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Core module for multi-tenant POS shop management',
    'description': """
        Core module for managing shops/tenants in a multi-tenant POS system.
        Provides:
        - Shop/tenant management
        - User role management (Owner, Manager, Cashier)
        - Multi-company support for data isolation
        - Base configuration settings
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail', 'product'],
    'data': [
        'security/pos_shop_security.xml',
        'security/ir.model.access.csv',
        'views/pos_shop_views.xml',
        'views/res_users_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}