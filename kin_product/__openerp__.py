# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html

{
    'name': 'Product Modifications',
    'version': '0.1',
    'category': 'product',
    'description': """
Product Modifications
=======================================================================================
""",
    'author': 'Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)',
    'website': 'http://kinsolve.com',
    'depends': ['base','product','stock','kin_account','operating_unit','stock_account','purchase','stock_inventory_revaluation'],
    'data': [
         'security/security.xml',
        'security/ir.model.access.csv',
        'cron_data.xml',
        'product.xml',
        'mail_template.xml',

    ],
    'test':[],
    'installable': True,
    'images': [],
}