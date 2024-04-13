# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Mattobell (<http://www.mattobell.com>)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import fields, models, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi#odoo9
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'is_deferred_account' : True})
        return res

class AccountAccount(models.Model):
    _inherit = 'account.account'
    is_deferred_account = fields.Boolean('Deferred Account?')
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi#odoo9
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.product_id.is_deffered_income:
            if self.product_id.is_deffered_income and not self.product_id.property_deferred_account_id:
                raise UserError(_('Please define deffered income account on product form under accounting tab.'))
            account_id = self.product_id.property_deferred_account_id.id
            res.update({'account_id': account_id})
        else:
            pass
        return res
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def _get_def_account(self):
        if self._context.get('type') and self._context['type'] == 'out_invoice':
            return True
        return False
    
    is_deferred_account = fields.Boolean('Deferred Account?', default=_get_def_account)
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.v8#odoo9
    def get_invoice_line_account(self, type, product, fpos, company):
        res = super(AccountInvoiceLine, self).get_invoice_line_account(type, product, fpos, company)
        if self.invoice_id.is_deferred_account and type == 'out_invoice' and product:
            if product.is_deffered_income:
                return product.property_deferred_account_id
        return res
    
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    is_deferred_account = fields.Boolean('Reverse Deferred Income')
    deferred_account_id = fields.Many2one('account.account', 'Deferred Income')
    sale_account_id = fields.Many2one('account.account', 'Sales Income')
    deferred_move_id = fields.Many2one('account.move', 'Deferred Journal Entry', readonly=True)
    deferred_journal_id = fields.Many2one('account.journal', 'Sales Journal')
    credit_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account - Deferred Entry')
    
    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            deferred_account_id = False
            sale_account_id = False
            invoice = self.env['account.invoice'].browse(invoice['id'])
            for line in invoice.invoice_line_ids:
                if line.account_id:
                    deferred_account_id = line.account_id.id  
                    fpos = invoice.fiscal_position_id
                    company = invoice.company_id
                    account = self.env['account.invoice.line'].get_invoice_line_account('out_invoice', line.product_id, fpos, company)
                    sale_account_id = account.id
                    break
            rec.update({
                'is_deferred_account': invoice.is_deferred_account,
                'deferred_account_id': deferred_account_id,
                'sale_account_id': sale_account_id,
                'deferred_journal_id': invoice.journal_id.id
            })
        return rec

#     @api.model
#     def default_get(self, fields):
#         rec = super(AccountPayment, self).default_get(fields)
#         context = dict(self._context or {})
#         active_model = context.get('active_model')
#         active_ids = context.get('active_ids')
#         
#         invoices = self.env[active_model].browse(active_ids)
#         rec.update({
#             'is_deferred_account': invoices[0].is_deferred_account,
#         })
#         return rec
#     
    @api.model
    def create_deferred_move(self):
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        for payment in self:
            if not payment.sale_account_id or not payment.deferred_account_id:
                raise UserError(_('Please select the Deferred Income and Sales Income.'))
            if not payment.deferred_journal_id:
                raise UserError(_('Please select the Sales Journal.'))
 
            move_vals = {
                'date' : payment.payment_date,
                'ref' : payment.communication or payment.name or '',
                'journal_id': payment.deferred_journal_id.id,
                'name' :  payment.name
            }
            move_id = move_pool.create(move_vals)
            payment.write({'deferred_move_id': move_id.id})
            company_currency = payment.company_id.currency_id
            current_currency = payment.currency_id
            sign = payment.deferred_journal_id.type == 'purchase' and 1 or -1
            if payment.amount > 0.0:
                amount = company_currency.compute(payment.amount, current_currency)
                vals11 = []
                vals11.append((0,0, {
                    'name':payment.name,
                    'debit': 0.0,
                    'credit': amount,
                    'account_id': payment.sale_account_id.id,
                    'move_id': move_id.id,
                    'journal_id': payment.deferred_journal_id.id,
                    'partner_id': payment.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': company_currency <> current_currency and - sign * amount or 0.0,
                    'date': payment.payment_date,
                    'analytic_account_id': payment.credit_analytic_id.id,
                }))
                vals11.append((0,0,{
                    'name': payment.name,
                    'debit': amount,
                    'credit': 0.0,
                    'account_id': payment.deferred_account_id.id,
                    'move_id': move_id.id,
                    'journal_id': payment.deferred_journal_id.id,
                    'partner_id': payment.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency':  company_currency <> current_currency and sign * amount or 0.0,
                    'date': payment.payment_date,
                }))
                move_id.write({'line_ids': vals11})
        return True
    
    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        #If voucher has Reverse Deferred Income Ticked then it will creates the extra journal entries for deferred Accounts
        if self.is_deferred_account:
            self.create_deferred_move()
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
