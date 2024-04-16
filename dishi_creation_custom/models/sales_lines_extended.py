import openerp
from openerp import models, fields, api


class SalesLinesExtend(models.Model):
    _inherit = 'sale.order.line'

    product_commission = fields.Many2one('product.commission.type', string='Commission Type')
    commission_value = fields.Float(string='Commission (%)')
    commission_amount = fields.Float(string='Amount (Comm)', store=True, digits=(16, 4))
    fx_rates = fields.Float(store=True, digits=(16, 4))

    @api.onchange('product_id', 'product_commission')
    def onchange_product_id(self):
        if self.product_id:
            commission_type = self.product_id.product_commission
            self.product_commission = commission_type
            self.commission_value = commission_type.value_percentage

    @api.depends('product_commission')
    def onchange_product_commission(self):
        if self.product_commission:
            commission_type = self.product_id.product_commission
            self.commission_value = commission_type.value_percentage

    @api.onchange('price_subtotal')
    def change_margin1(self):
        for rec in self:
            mr = (rec.price_unit - rec.purchase_price) * rec.product_uom_qty
            comm_amt = (mr * rec.commission_value) / 100
            rec.commission_amount = comm_amt
            rec.margin = mr
