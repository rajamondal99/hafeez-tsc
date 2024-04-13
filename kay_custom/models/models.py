# -*- coding: utf-8 -*-

from openerp import models, fields, api

class kay_custom(models.Model):
    _inherit = 'res.company'

    x_time_start = fields.Datetime(string='Timeout Implementation Start Date')

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
