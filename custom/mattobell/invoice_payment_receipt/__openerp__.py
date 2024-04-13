# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Print Payment Receipt - by Invoice',
    'summary': 'Print Payment Receipt - by Invoice in Odoo 9',
    'version':'1.0',
    'price': 50.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category':'Accounting & Finance',
    'description': """
                Invoice Payment Receipt Report:
                    - Creating Invoice Payment Receipt Report
                    - Sent payment receipt to customer by email.
                    - Customer payment receipt odoo 9 
                    - Invoice payment receipt
                    - Invoice  payments.
                Payment receipt print odoo 9
            """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['account'],
    'data':[
            'report/invoice_payment_receipt_report.xml',
            'view/payment_receipt.xml',
            'view/payment_receipt_data.xml'],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
