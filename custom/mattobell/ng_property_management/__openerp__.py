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
    'name':'Property Management',
    'Version':'1.0',
    'Category':'Property Management',
    'description': """
                Property Management:
                    - Adding New Field
            """,
    'author': "Mattobell",
    'website': 'http://www.mattobell.com',

    'depends': ['sale',
                'purchase',
                'crm',
                ],
    'data':['security/ir.model.access.csv',
            'security/security.xml',
            'views/sale_view.xml',
            'views/agent_view.xml',
            'views/product_view.xml',
            'views/invoice_view.xml',
            'data/property_sequence.xml',
            'views/partner_sequence.xml',
            'data/product_sequence.xml',
            'views/branch_view.xml',
            'data/branch_sequence.xml',
            'views/report_invoice.xml',
#             'views/crm_view.xml',
            ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

