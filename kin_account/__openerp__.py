# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html

{
    'name': 'Account Modifications',
    'version': '0.1',
    'category': 'Accounting',
    'description': """
Account Modifications
=======================================================================================
""",
    'author': 'Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)',
    'website': 'http://kinsolve.com',
    'depends': ['base','account','account_asset','purchase','account_extra_reports','analytic','report'],
    'data': [
         'security/security.xml',
        'account_view.xml',
      #  'account_invoice_view.xml',
       # 'account_payment_view.xml',
        #'product_view.xml',
        #'wizard/account_report_partner_ledger_view.xml',
       # 'wizard/account_report_general_ledger_view.xml',
       # 'wizard/account_report_aged_partner_balance_view.xml',
        #'report/report_trialbalance.xml',
        #'report/account_invoice.xml',
        'sequence.xml',

    ],
    'test':[],
    'installable': True,
    'images': [],
}
