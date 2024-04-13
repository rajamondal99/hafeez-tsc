# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Mattobell (<http://www.mattobell.com>)

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
from openerp.osv import osv, fields

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'property_deferred_account_id': fields.property(
            model = 'account.account',
            type='many2one',
            relation='account.account',
            string="Deferred Income",
            view_load=True),
        'is_deffered_income': fields.boolean('Apply Deferred Income?', help='Tick this checkbox if this product has to be accounted as deffered account.'),
    }
    
product_template()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
