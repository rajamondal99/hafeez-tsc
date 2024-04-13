# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Mattobell (<http://www.mattobell.com>)
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
    'name' : 'Manage Subscriber Requests',
    'version': '1.0',
    'author': 'Mattobell',
    'website': 'http://www.mattobell.com',
    'description':'''
                This module allows to make request for create subscription.
    ''',
    'depends': [
              'ng_property_management',
              'crm'
               ],
    'data': ['security/subscription.xml','security/ir.model.access.csv',
             'views/customer_subscription.xml',
             'views/crm_lead_view.xml',
             'branch_sequence.xml',
             'report/customer_subscription.xml',
             'data/email_template.xml',
             ], 
    'installable':True,
    'auto_install':False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
