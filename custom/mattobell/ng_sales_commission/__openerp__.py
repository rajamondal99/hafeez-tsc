# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mattobell (<http://www.mattobell.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name':'Sales Commission',
    'Version':'1.0',
    'Category':'Sales Commission',
    'description': """
                Sales Commission:
                    - Adding New Menu Sales Commission in Accounting
                        - Sales Commission
                            - Sales Commission Report
                        - Sales Commission Invoice
            """,
    'author': "Mattobell",
    'website': 'http://www.mattobell.com',
    'depends': ['sale',
                'ng_property_management',
                'ng_deferred_income',
                'portal'],
    'data': ['views/sales_commission.xml',
             'views/sales_commission_sequence.xml',
             'report/sales_commission.xml',
             'security/ir.model.access.csv',
             'views/make_invoice.xml',
             'views/company_view.xml',
             'views/claim_view.xml',
             'data/claim_sequence.xml',
             'views/cheque_return_view.xml',
             'views/direct_branch_deposit_view.xml',
             'views/portal_commission_view.xml',
             'security/security.xml'],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

