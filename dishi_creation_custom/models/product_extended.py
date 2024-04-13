import openerp
from openerp import models, fields


class ProductTemplateExtend(models.Model):
    _inherit = 'product.template'

    product_commission = fields.Many2one('product.commission.type', string='Product Commission')
