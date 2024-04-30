from openerp import models, api
import math


class PaySlipLine(models.Model):
    _inherit = "hr.payslip.line"

    def create(self, cr, uid, values, context=None):
        if values.get('code') == 'NET':
            values['amount'] = math.ceil(values['amount'])
        return super(PaySlipLine, self).create(cr, uid, values, context=context)
