# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    send_payment_order = fields.Boolean(string='Send Receipt By Mail', help='Tick this box if you want to send payment receipt to this customer while validating customer payment. This will send email with payment report to customer on event of validating customer payment.')
