# -*- coding: utf-8 -*-

{
    'name': 'Common Modifications',
    'version': '0.1',
    'category': 'custom',
    'description': """ Common Modifications """,
    'author': 'Shon Puri (shonpuri@gmail.com, +91-9173765447)',
    'website': '',
    'depends': ['base', 'sale', 'purchase','stock'],
    'data': [
            'security/ir.model.access.csv',
            'views/view_product_commission.xml',
            'views/view_product_extended.xml',
            'views/view_sale_order_line_extended.xml',
            'views/view_account_invoice_extended.xml',

    ],
    'test': [],
    'installable': True,
    'images': [],
}
