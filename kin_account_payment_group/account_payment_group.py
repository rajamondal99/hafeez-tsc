# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html


from openerp import api, fields, models, _
from openerp.tools import amount_to_text


class AccountPaymentGroupExtend(models.Model):
    _inherit = 'account.payment.group'

    @api.multi
    def get_references(self):
        pay_list = []
        payment_ids = self.payment_ids
        for pay_line in payment_ids:
            if pay_line.ref_no:
                pay_list.append(pay_line.ref_no)
        return ', '.join(pay_list)

    @api.multi
    def get_paid_invoices(self):
        inv_list =[]
        matched_move_line_ids = self.matched_move_line_ids
        for matched_line in matched_move_line_ids :
            inv_list.append(matched_line.invoice_id.number)
        return ', '.join(inv_list)


    @api.multi
    def amount_to_text(self, amt, currency=False):
        dd = self.mapped('matched_move_line_ids')
        ddd = list(set(dd))
        big = ''
        small = ''
        if currency.name == 'NGN':
            big = 'Naira'
            small = 'kobo'
        elif currency.name == 'USD':
            big = 'Dollar'
            small = 'Cent'
        else:
            big = 'Naira'
            small = 'kobo'

        amount_text = amount_to_text(amt, currency).replace('euro', big).replace('Cent', small)
        return str.upper('**** ' + amount_text + '**** ONLY')

    @api.multi
    def post(self):
        res = super(AccountPaymentGroupExtend, self).post()
        if not self.name:
            self.name = self.env['ir.sequence'].get('receipt_id_code')
        return res

    name = fields.Char(string='Receipt Number', readonly=True, states={'draft': [('readonly', False)]})


