# -*- coding: utf-8 -*-

import time

from openerp.osv import osv
from openerp.report import report_sxw
from openerp import pooler

class account_payment_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_payment_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
              'time': time,
                                  })
    
    def _voucher_line_get(self, payment):
        domain = []
        payment_obj = pooler.get_pool(self.cr.dbname).get('account.payment')
        domain.append(('id','=',payment.id))
        payment_ids = payment_obj.search(self.cr, self.uid, domain, context=self.context)
        return payment_obj.browse(self.cr, self.uid, payment_ids, context=self.context)
    
class report_test(osv.AbstractModel):
    _name = "report.account_payment_report.print_payment_report"
    _inherit = "report.abstract_report"
    _template = "account_payment_report.print_payment_report"
    _wrapped_report_class = account_payment_report

