# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Customer/Supplier Statement',
    'version': '1.0',
    'price': 25.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Accounting & Finance',
    'summary': 'Customer/Supplier Statement on Customer/Supplier list/form',
    'description': """
This module add report on customer/supplier form to print customer/supplier statement report same like partner ledger.

Tags:
account customer statement
customer statement report
partner statement
partner ledger
customer ledger
supplier ledger
receivable statement
 """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['account_extra_reports'],
    'data': [
            'wizard/account_report_partner_ledger_view.xml',
            'views/report_partnerledger.xml',
            'views/report.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
