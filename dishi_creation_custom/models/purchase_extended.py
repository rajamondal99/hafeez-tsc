from openerp import models, fields, api
from datetime import datetime


class PurchaseExtend(models.Model):
    _inherit = 'purchase.order'



    @api.onchange('sale_order_id')
    def _compute_order_lines(self):
        request_obj = self.env['sale.order']
        requests = request_obj.search([('id', "=", self.sale_order_id.id)])
        lines = []
        for request in requests.order_line:
            lines.append((0, 0, {
                'product_id': request.product_id.id,
                'product_qty': request.product_uom_qty,
                'date_required': fields.datetime.today(),
                'product_uom_id': request.product_id.uom_id.id,

            })
                         )
        self.line_ids = lines
