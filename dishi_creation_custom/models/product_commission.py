import openerp
from openerp import api, tools, SUPERUSER_ID, models, fields


class ProductCommission(models.Model):
    _name = 'product.commission.type'
    _description = 'Product Commission'

    name = fields.Char()
    value_percentage = fields.Float(string="Value Percentage(%)")

