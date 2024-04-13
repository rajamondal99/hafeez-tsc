# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class product_product(models.Model):
    _inherit = 'product.product'
    
    surcharge = fields.Float(string='Surcharge (%)')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: