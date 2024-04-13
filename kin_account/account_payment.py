# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html
from openerp import api, fields, models, _
from openerp.tools.float_utils import float_compare
from urllib import urlencode
from urlparse import urljoin
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError, RedirectWarning, ValidationError
from openerp.tools import amount_to_text

class AccountPaymentExtend(models.Model):
    _inherit = 'account.payment'

    ref_no = fields.Char(string='Reference No')






