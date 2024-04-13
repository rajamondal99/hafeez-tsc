# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class ChequeReturn(models.Model):
    _name = 'cheque.return'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    @api.model
    def _default_currency(self):
        company = self.env.user.company_id
        return company.currency_id.id
    
    name = fields.Char('Name',required=True, copy=False)
    cheque_number = fields.Char('Cheque Number',required=True, copy=False)
    customer_id = fields.Many2one('res.partner', 'Customer',required=True, domain=[('customer', '=', True)])
    date = fields.Date('Date',required=True, default=fields.Date.today())
    journal_id = fields.Many2one('account.journal', 'Payment Method',required=True)
    revenue_journal_id = fields.Many2one('account.journal', 'Payment Method(Revenue)',required=True)
    deferred_journal_id = fields.Many2one('account.journal', 'Payment Method(Deferred)',required=True)
    cheque_amount = fields.Float('Cheque Amount',required=True)
    return_charge = fields.Float('Cheque Return Charge',required=True)
    return_account_id = fields.Many2one('account.account', 'Return Cheque Account',required=True)
    revenue_account_id = fields.Many2one('account.account', 'Revenue Account',required=True)
    deferred_account_id = fields.Many2one('account.account', 'Deferred Income Account',required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('validate', 'Validated')], string="State",
                             default="draft",
                              track_visibility="onchange", readonly=True)
    company_id = fields.Many2one('res.company', 'Company',required=True,
                default=lambda self: self.env['res.company']._company_default_get('cheque.return'))
    currency_id = fields.Many2one('res.currency', 'Currency',default=_default_currency)
    invoice_id = fields.Many2one('account.invoice', 'Invoice Ref',readonly=True, copy=False)
    revenue_move_id = fields.Many2one('account.move', 'Journal Entry(Revenue)', readonly=True, copy=False)
    deferred_move_id = fields.Many2one('account.move', 'Journal Entry(Deferred)', readonly=True, copy=False)

    @api.multi
    def action_validate(self):
        for cheque in self:
            lines = [(0,0,{'name' :  "Cheque Returned Charges", 
                'origin':  '/',
                'sequence':  '',
                'uos_id':  False,
                'product_id':  False,
                'account_id':  cheque.return_account_id.id, 
                'price_unit':  cheque.return_charge,
                'quantity' : 1 , 
                'price_subtotal':  cheque.return_charge,  
                'discount' :0,
                'partner_id':  cheque.customer_id.id })]
            vals = {'date_invoice': cheque.date,
                    'partner_id': cheque.customer_id.id,
                    'account_id': cheque.customer_id.property_account_receivable_id.id,
                    'invoice_line_ids': lines,
                    'type': 'out_invoice',
                    'name': cheque.cheque_number,
                    'journal_id': cheque.journal_id.id,
                    'company_id': cheque.company_id.id,
                    'currency_id': cheque.currency_id.id
                }
            #create invoice for cheque return charges by bank
            invoice_id = self.env['account.invoice'].create(vals)
            
            move_obj = self.env['account.move']
            #create common move vals for both move
            common_move_vals = {
                'date': cheque.date,
                'ref': cheque.cheque_number,
                'partner_id': cheque.customer_id.id,
                'company_id': cheque.company_id.id
            }

            company_currency = cheque.company_id.currency_id
            current_currency = cheque.currency_id
            ctx = self._context.copy()
            ctx.update({'date': cheque.date})
            amount = current_currency.compute(cheque.cheque_amount, company_currency)
            
            if cheque.revenue_journal_id.type == 'purchase':
                revenue_sign = 1
            else:
                revenue_sign = -1
            
            #create common credit move line vals
            common_credit_line = {
                'name': 'Cheque Return',
                'ref': cheque.cheque_number,
                'debit': 0.0,
                'credit': amount,
                'journal_id': False,
                'partner_id': cheque.customer_id.id,
                'currency_id': company_currency.id <> current_currency.id and current_currency.id or False,
                'date': cheque.date,
            }
            #create common debit move line vals
            common_debit_line = {
                'name': 'Cheque Return',
                'ref': cheque.cheque_number,
                'credit': 0.0,
                'debit': amount,
                'journal_id': False,
                'partner_id': cheque.customer_id.id,
                'currency_id': company_currency.id <> current_currency.id and  current_currency.id or False,
                'date': cheque.date,
            }
            #Create move for revenue
            revenue_move_vals = {'journal_id': cheque.revenue_journal_id.id}
            revenue_move_vals.update(common_move_vals)
            revenue_move_id = move_obj.create(revenue_move_vals)
            
            revenue_credit_line = {'account_id': cheque.journal_id.default_credit_account_id.id,
                                   'journal_id': cheque.revenue_journal_id.id,
                                   'amount_currency': company_currency.id <> current_currency.id and -revenue_sign * cheque.cheque_amount or 0.0,
                                   'move_id': revenue_move_id.id,}
            revenue_credit_line.update(common_credit_line)
            revenue_debit_line = {'account_id': cheque.revenue_account_id.id,
                                  'journal_id': cheque.revenue_journal_id.id,
                                  'amount_currency': company_currency.id <> current_currency.id and revenue_sign * cheque.cheque_amount or 0.0,
                                  'move_id': revenue_move_id.id,}
            revenue_debit_line.update(common_debit_line)
            return_move_line_vals = [(0, 0, revenue_credit_line), (0, 0, revenue_debit_line)]
            revenue_move_id.write({'line_ids': return_move_line_vals})
            
            #Create move for deferred
            
            if cheque.deferred_journal_id.type == 'purchase':
                deferred_sign = 1
            else:
                deferred_sign = -1
            
            deferred_move_vals = {'journal_id': cheque.deferred_journal_id.id}
            deferred_move_vals.update(common_move_vals)
            deferred_move_id = move_obj.create(deferred_move_vals)
            
            deferred_credit_line = {'account_id': cheque.deferred_account_id.id,
                                    'journal_id': cheque.deferred_journal_id.id,
                                    'amount_currency': company_currency.id <> current_currency.id and -deferred_sign * cheque.cheque_amount or 0.0,
                                    'move_id': deferred_move_id.id,}
            deferred_credit_line.update(common_credit_line)
            deferred_debit_line = {'account_id': cheque.customer_id.property_account_receivable_id.id,
                                   'journal_id': cheque.deferred_journal_id.id,
                                   'amount_currency': company_currency.id <> current_currency.id and deferred_sign * cheque.cheque_amount or 0.0,
                                   'move_id': deferred_move_id.id,}
            deferred_debit_line.update(common_debit_line)
            deferred_move_line_vals = [(0, 0, deferred_credit_line), (0, 0, deferred_debit_line)]
            deferred_move_id.write({'line_ids': deferred_move_line_vals})
            
            cheque.write({'state': 'validate', 
                          'invoice_id': invoice_id.id,
                          'revenue_move_id': revenue_move_id.id,
                          'deferred_move_id': deferred_move_id.id
                          })
            return True
            
