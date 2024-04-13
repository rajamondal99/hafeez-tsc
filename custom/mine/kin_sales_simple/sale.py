# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT




class SaleOrderExtend(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Order"

    @api.multi
    def action_make_payment(self):

        return


    @api.multi
    def action_do_delivery(self):

        return


class SaleOrderPaymentWizard(models.TransientModel):
    """Refunds invoice"""

    _name = "sale.order.payment.wizard"