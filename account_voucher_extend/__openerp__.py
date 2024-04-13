# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Cash Transactions ',
    'version' : '1.0',
    'summary': 'Manage your debts and credits thanks to simple sale/purchase receipts',
    'description': """
TODO

    """,
    'category': 'Accounting & Finance',
    'sequence': 20,
    'depends' : ['account','product'],
    'demo' : [],
    'data' : [
        'account_voucher_view.xml',
        'voucher_sales_purchase_view.xml',
        'account_voucher_data.xml',
        'security/ir.model.access.csv',
    ],

    'auto_install': False,
    'installable': True,
}
