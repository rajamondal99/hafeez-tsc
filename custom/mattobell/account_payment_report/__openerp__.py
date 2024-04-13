# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Customer Payment Receipt Report',
    'version': '1.0',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'license': 'Other proprietary',
    'category' : 'Accounting & Finance',
    'website': 'https://www.probuse.com',
    'price': 25.0,
    'currency': 'EUR',
    'description': ''' 
    Account Payment Report
- Customer Payment Receipt Report
- Print receipt
- Print Payment
- Payments report
  ''',
    'depends':['account'],
    'data' : [
              'views/res_partner_view.xml',
              'views/payment_report_view.xml',
              'views/payment_report_reg.xml',
              'data/payment_email.xml',
              ],
    'installable':True,
    'auto_install':False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
