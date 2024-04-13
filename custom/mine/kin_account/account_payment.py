# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
    #     """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
    #     """
    #     res = super(AccountPayment,self)._get_shared_move_line_vals( debit, credit, amount_currency, move_id, invoice_id=invoice_id)
    #
    #     journal_id = self.journal_id or False
    #     if journal_id :
    #         if self.payment_type == 'inbound' and credit != 0 or self.payment_type == 'outbound' and debit != 0 :
    #             analytic_account_id = journal_id.analytic_account_id
    #
    #             if analytic_account_id :
    #                 res.update({'analytic_account_id':analytic_account_id.id})
    #
    #     return res


    # def _get_liquidity_move_line_vals(self, amount):
    #
    #     vals = super(AccountPayment,self)._get_liquidity_move_line_vals(amount=amount)
    #
    #     journal_id = self.journal_id or False
    #     if journal_id :
    #         analytic_account_id = journal_id.analytic_account_id
    #
    #         if analytic_account_id :
    #             vals.update({'analytic_account_id':analytic_account_id.id})
    #
    #     return vals
