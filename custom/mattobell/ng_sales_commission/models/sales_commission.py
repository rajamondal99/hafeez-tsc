# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class ResCompany(models.Model):
    _inherit = 'res.company'

    expense_account_id = fields.Many2one('account.account', 'Marketing Expense Account')


class SalesCommission(models.Model):
    _name = 'sales.commission'
    _description = "Sales Commission"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'number'

    @api.onchange('sales_agent_id')
    def onchange_agent(self): 
        if self.sales_agent_id:
            agent_partner_ref = self.env['sales.agent.partner'].search([('agent_id', '=', self.sales_agent_id.id)])
            if agent_partner_ref:
                self.sales_person_id = agent_partner_ref.user_id.id

    @api.depends('invoice_id','invoice_id.amount_total','invoice_id.residual' )
    def _paid_amount(self):
        for line in self:
            line.customer_paid_amount = line.invoice_id.amount_total - line.invoice_id.residual

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('sales.commission')
        vals['number'] = seq
        return super(SalesCommission,self).create(vals)

    @api.depends('commision_invoice_ids', 'commision_invoice_ids.amount')
    def _compute_agent_received_amount(self):
        for commision in self:
            for line in commision.commision_invoice_ids:
                commision.agent_received_amount += line.amount
                
                
    @api.depends('commision_invoice_ids', 'commision_invoice_ids.state','commision_invoice_ids.paid_amount', 'invoice_amount')
    def _compute_state(self):
        for commision in self:
            total_paid_amount = 0.0
            commision.state = 'draft'
            for line in commision.commision_invoice_ids:
                total_paid_amount += line.paid_amount
            if total_paid_amount > 0:
                if total_paid_amount == commision.invoice_amount:
                    commision.state = 'paid'
                elif total_paid_amount > 0 and total_paid_amount < commision.invoice_amount:
                    commision.state = 'partial_paid'

    number = fields.Char(readonly=True)
    sales_agent_id = fields.Many2one('sales.agent', string='Marketer', required=True)
    sales_person_id = fields.Many2one('res.users', string='Sales Person', required=True)
    date = fields.Date(string='Date', default=fields.Date.today())
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    invoice_amount = fields.Float(string='Invoice Amount')
    agent_commision = fields.Float('Marketer Commision(%)')
    customer_paid_amount = fields.Float(string='Customer Paid Amount', compute='_paid_amount')
    agent_received_amount = fields.Float(string='Marketer Received Amount', compute="_compute_agent_received_amount", store=True)
    state = fields.Selection([('draft', 'New'), ('partial_paid', 'Partial Paid'),
                              ('paid', 'Paid')], string="State", compute="_compute_state", 
                             default='draft', track_visibility="onchange")
    commision_invoice_ids = fields.One2many('sales.commission.invoice', 'sales_commission_id', string="Sales Commision Invoice")
    commisionable_amount = fields.Float('Total Commissionable Amount')


class SalesCommissionInvoice(models.Model):
    _name = 'sales.commission.invoice'
    _description = "Sales Commission Invoice"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    sales_commission_id = fields.Many2one('sales.commission', string='Sales Commission')
    amount = fields.Float(string='Commission Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    date = fields.Date(string='Date', default=fields.Date.today(), required=True)
    agent_commision = fields.Float('Marketer Commision(%)')
    is_invoiced = fields.Boolean('Invoiced?')
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('approve','Approved'),('reject','Rejected'),('paid','Invoiced'),('cancel','Cancelled')], 
                             readonly=True, default='draft', track_visibility='onchange', copy=False)
    invoice_id = fields.Many2one('account.invoice', 'Marketer Invoice')
    payment_id = fields.Many2one('account.payment', 'Customer Payment', readonly=True)
    paid_amount = fields.Float('Customer Paid Amount', readonly=True)
    journal_id = fields.Many2one('account.journal', 'Marketing Commission Journal',
                                readonly=True,
                                domain=[('type', '=', 'purchase')],
                                states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    revenue_account_id = fields.Many2one('account.account', 'Expense/Marketing  Account',
                                         readonly=True,
                                         states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    marketer_account_id = fields.Many2one('account.account', 'Marketer Account',
                                          readonly=True,
                                         states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
#     cash_bank_account_id = fields.Many2one('account.account', 'Cash/Bank Account')
    move_id = fields.Many2one('account.move', 'Journal Entry')
    unpaid_move_id = fields.Many2one('account.move', 'Unpaid Journal Entry')
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('sales.commission.invoice'))

    @api.onchange('sales_commission_id')
    def onchange_sales_commission_id(self):
        for commission in self:
            commission.agent_commision = commission.sales_commission_id.agent_commision or 0.0

    @api.one
    def confirm_sales_commission(self):
        self.state = 'confirm'

    @api.one
    def cancel_sales_commission(self):
        self.state = 'cancel'

    @api.multi
    def approved_sales_commission(self):
        for commission in self:
            if False:#no need to create any move here.
                if not commission.journal_id:
                    raise Warning(_('Please select Journal.'))
                if not commission.revenue_account_id:
                    raise Warning(_('Please select Revenue Account.'))
                if not commission.marketer_account_id:
                    raise Warning(_('Please select Marketer Account.'))
                
                move_vals = {
                    'date' : commission.date,
                    'ref' : commission.sales_commission_id.number or '',
                    'journal_id': commission.journal_id.id,
                    'name' :  commission.sales_commission_id.number
                }
                move_id = self.env['account.move'].create(move_vals)
                commission.write({'move_id': move_id.id})
                company_currency = commission.company_id.currency_id
                current_currency = commission.currency_id
                sign = commission.journal_id.type == 'purchase' and 1 or -1
                if commission.amount > 0.0:
                    amount = company_currency.compute(commission.amount, current_currency)
                    move_line_vals = []
                    move_line_vals.append((0,0, {
                        'name':commission.sales_commission_id.number,
                        'debit': 0.0,
                        'credit': amount,
                        'account_id': commission.marketer_account_id.id,
                        'move_id': move_id.id,
                        'journal_id': commission.journal_id.id,
                        'partner_id': False,
                        'currency_id': company_currency <> current_currency and  current_currency or False,
                        'amount_currency': company_currency <> current_currency and - sign * amount or 0.0,
                        'date': commission.date,
                        'analytic_account_id': False,
                    }))
                    move_line_vals.append((0,0,{
                        'name': commission.sales_commission_id.number,
                        'debit': amount,
                        'credit': 0.0,
                        'account_id': commission.revenue_account_id.id,
                        'move_id': move_id.id,
                        'journal_id': commission.journal_id.id,
                        'partner_id': False,
                        'currency_id': company_currency <> current_currency and  current_currency or False,
                        'amount_currency':  company_currency <> current_currency and sign * amount or 0.0,
                        'date': commission.date,
                    }))
                    move_id.write({'line_ids': move_line_vals})
            commission.state = 'approve'

    @api.one
    def reject_sales_commission(self):
        self.state = 'reject'

    @api.multi
    def paid_sales_commission(self):
        for commission in self:
            if False:#no need to create any move here.
                if not commission.journal_id:
                    raise Warning(_('Please select Journal.'))
                if not commission.marketer_account_id:
                    raise Warning(_('Please select Marketer Account.'))
                
                move_vals = {
                    'date' : commission.date,
                    'ref' : commission.sales_commission_id.number or '',
                    'journal_id': commission.journal_id.id,
                    'name' :  commission.sales_commission_id.number
                }
                move_id = self.env['account.move'].create(move_vals)
                commission.write({'unpaid_move_id': move_id.id})
                company_currency = commission.company_id.currency_id
                current_currency = commission.currency_id
                sign = commission.journal_id.type == 'purchase' and 1 or -1
                if commission.amount > 0.0:
                    amount = company_currency.compute(commission.amount, current_currency)
                    move_line_vals = []
                    move_line_vals.append((0,0, {
                        'name':commission.sales_commission_id.number,
                        'debit': 0.0,
                        'credit': amount,
                        'account_id': commission.journal_id.default_credit_account_id.id,
                        'move_id': move_id.id,
                        'journal_id': commission.journal_id.id,
                        'partner_id': False,
                        'currency_id': company_currency <> current_currency and  current_currency or False,
                        'amount_currency': company_currency <> current_currency and - sign * amount or 0.0,
                        'date': commission.date,
                        'analytic_account_id': False,
                    }))
                    move_line_vals.append((0,0,{
                        'name': commission.sales_commission_id.number,
                        'debit': amount,
                        'credit': 0.0,
                        'account_id': commission.marketer_account_id.id,
                        'move_id': move_id.id,
                        'journal_id': commission.journal_id.id,
                        'partner_id': False,
                        'currency_id': company_currency <> current_currency and  current_currency or False,
                        'amount_currency':  company_currency <> current_currency and sign * amount or 0.0,
                        'date': commission.date,
                    }))
                    move_id.write({'line_ids': move_line_vals})
            commission.action_make_supplier_invoice()
            #if commission.invoice_id.state != 'paid':
            #    raise Warning('Please generate Agent/Marketers Invoice.')
            commission.state = 'paid'
    

    @api.one
    def draft_sales_commission(self):
        self.state = 'draft'

    @api.model
    def action_make_supplier_invoice(self):
        #active_ids = self.env.context.get('active_ids')
        #invoice_commision_ids = self.browse(active_ids)
        company = self.env.user.company_id
        for commision in self:
            if commision.is_invoiced:
                raise Warning('Invoice already created.')
            if not company.expense_account_id:
                raise Warning('Please configure expense account on company form.')
            if commision.state in ('draft', 'confirm', 'cancel', 'reject'):
                raise Warning('You can not create invoice in %s state.' %(commision.state))
            agent_id = commision.sales_commission_id.sales_agent_id
            
            partner_agent = self.env['sales.agent.partner'].search([('agent_id', '=', agent_id.id)])
            journal_ids = self.env['account.journal'].search([('type', '=', 'purchase'), 
                                ('company_id', '=', company.id)],limit=1).ids
                                
            journal_id = journal_ids[0]
            lines = [(0,0,{'name' :  "Invoice Commision Bonus", 
                'origin':  '/',
                'sequence':  '',
                'uos_id':  False,
                'product_id':  False,
                'account_id':  company.expense_account_id.id, 
                'price_unit':  commision.amount,
                'quantity' : 1 , 
                'price_subtotal':  commision.amount,  
                'discount' :0,
                'partner_id':  partner_agent.partner_id.id })]
            vals = {'date_invoice': commision.date,
                    'partner_id': partner_agent.partner_id.id,
                    'account_id': partner_agent.partner_id.property_account_payable_id.id,
                    'invoice_line_ids': lines,
                    'type': 'in_invoice',
                    'name': ' ',
                    'journal_id': journal_id,
                    'company_id': company.id
                }
            invoice_id = self.env['account.invoice'].create(vals)
            commision.is_invoiced = True
            commision.write({'invoice_id': invoice_id.id})

    @api.model
    def action_make_supplier_invoice_wizard(self):
        active_ids = self.env.context.get('active_ids')
        invoice_commision_ids = self.browse(active_ids)
        company = self.env.user.company_id
        for commision in invoice_commision_ids:
            if commision.is_invoiced:
                raise Warning('Invoice already created.')
            if not company.expense_account_id:
                raise Warning('Please configure expense account on company form.')
            if commision.state in ('draft', 'confirm', 'cancel', 'reject'):
                raise Warning('You can not create invoice in %s state.' %(commision.state))
            agent_id = commision.sales_commission_id.sales_agent_id
            
            partner_agent = self.env['sales.agent.partner'].search([('agent_id', '=', agent_id.id)])
            journal_ids = self.env['account.journal'].search([('type', '=', 'purchase'), 
                                ('company_id', '=', company.id)],limit=1).ids
                                
            journal_id = journal_ids[0]
            lines = [(0,0,{'name' :  "Invoice Commision Bonus", 
                'origin':  '/',
                'sequence':  '',
                'uos_id':  False,
                'product_id':  False,
                'account_id':  company.expense_account_id.id, 
                'price_unit':  commision.amount,
                'quantity' : 1 , 
                'price_subtotal':  commision.amount,  
                'discount' :0,
                'partner_id':  partner_agent.partner_id.id })]
            vals = {'date_invoice': commision.date,
                    'partner_id': partner_agent.partner_id.id,
                    'account_id': partner_agent.partner_id.property_account_payable_id.id,
                    'invoice_line_ids': lines,
                    'type': 'in_invoice',
                    'name': ' ',
                    'journal_id': journal_id,
                    'company_id': company.id
                }
            invoice_id = self.env['account.invoice'].create(vals)
            commision.is_invoiced = True
            commision.write({'invoice_id': invoice_id.id})
            commision.state = 'paid'


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    agent_commision = fields.Float('Marketer Commission(%)')

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    apply_sales_commission = fields.Boolean(string='Apply Sales Commission?', default=False, readonly=True ,states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
    invoice_commision_id = fields.Many2one('sales.commission.invoice', 'Ref Invoice Commission')
    agent_commision = fields.Float('Marketer Commission(%)')
    
    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice,self).invoice_validate()
        commission_inv_obj = self.env['sales.commission']
        commission_inv_id = []
        for invoice in self:
            user = invoice.user_id and invoice.user_id.id or self.env.user.id
            if invoice.user_id.id:
                commisionable_amount = 0.0
                
                for line in invoice.invoice_line_ids:
                    if line.agent_commision > 0.0:
                        commisionable_amount += line.price_subtotal
#             if invoice.apply_sales_commission:
                commission_inv_vals = {
                        'sales_agent_id': invoice.user_id.id,
                        'sales_person_id': user,
                        'date': invoice.date_invoice,
                        'invoice_id': invoice.id,
                        'invoice_amount': invoice.amount_total,
                        'agent_commision': invoice.agent_commision,
                        'commisionable_amount': commisionable_amount
                        }
                commission_inv_id = commission_inv_obj.create(commission_inv_vals)
        return res


class Sale(models.Model):
    _inherit = 'sale.order'

    apply_sales_commission = fields.Boolean(string='Apply Sales Commission?', copy=True, default=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    agent_commision = fields.Float('Commission(%)', copy=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    
    
    @api.multi
    def set_commission(self):
        for record in self:
            if record.apply_sales_commission:
                for line in record.order_line:
                    if not line.agent_commision:
                        line.agent_commision = record.agent_commision
    
    @api.multi
    def action_confirm(self):
        for order in self:
            if order.apply_sales_commission:
                for ord_line in order.order_line:
                    if not ord_line.agent_commision:
                        raise Warning(_('Marketer commission must be greater then zero.'))
        return super(Sale, self).action_confirm()
    
    @api.multi
    def _prepare_invoice(self):
        result = super(Sale, self)._prepare_invoice()
        apply_sales_commission = self.apply_sales_commission
        result.update({'apply_sales_commission' : apply_sales_commission,
                       'agent_commision': self.agent_commision})
        return result


class PaymentCommissionLine(models.Model):
    _name = 'payment.commission.line'
    
    payment_id = fields.Many2one('account.payment', 'Payment')
    invoice_line_id = fields.Many2one('account.invoice.line', 'Invoice Line')
    property_ref = fields.Many2one('sale.property.reference', 'Property Reference')
    line_amount = fields.Float('Line Amount')
    amount = fields.Float('Amount')
    agent_commision = fields.Float('Commission(%)')
    
    
    @api.onchange('invoice_line_id')
    def onchange_invoice_line(self):
        for line in self:
            line.property_ref = line.invoice_line_id.preoperty_ref_id.id
            line.line_amount = line.invoice_line_id.price_subtotal
            line.agent_commision = line.invoice_line_id.agent_commision
    
    
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('commission_ids', 'commission_ids.amount')
    def _compute_total_amount(self):
        for payment in self:
            for line in payment.commission_ids:
                payment.total_amount += line.amount

    apply_sales_commission = fields.Boolean(string='Apply Sales Commission?', copy=True, default=False, readonly=False)
    sales_commision_id = fields.Many2one('sales.commission', string="Sales Commision")
    agent_commision = fields.Float('Marketer Commision(%)')
    sale_person_id = fields.Many2one('res.users', 'Sales Person')
    property_ref_ids = fields.Many2many('sale.property.reference',
                                        'property_reference_payment_rel'
                                        'claim_id', 'property_ref_id',
                                        string="Property Lines")
    commission_ids = fields.One2many('payment.commission.line', 'payment_id', 'Commission Lines')
    total_amount = fields.Float(compute='_compute_total_amount', string='Total Amount', store=True)
    sales_agent_id = fields.Many2one('sales.agent', string='Marketer', required=False)
    
    
    @api.onchange('sales_agent_id')
    def onchange_sales_agent_id(self):
        for rec in self:
            if rec.sales_agent_id:
                agent_partner_ids = self.env['sales.agent.partner'].search([('agent_id', '=', rec.sales_agent_id.id)])
                user_ids = [partner.user_id.id for partner in agent_partner_ids]
                rec.sale_person_id = user_ids and user_ids[0] or False
                return {'domain': {'sale_person_id': [('id', 'in', user_ids)]}}
        
    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            sale_commision = self.env['sales.commission'].search([('invoice_id', '=', invoice['id'])])
            rec.update(sale_person_id = invoice['user_id'] and invoice['user_id'][0] or False,
                       sales_commision_id = sale_commision.id,
                       sales_agent_id = invoice['agent_id'] and invoice['agent_id'][0] or False)
        return rec

    @api.onchange('sale_person_id')
    def onchange_sale_person_id(self):
        self.sales_commision_id = False
        sales_commisions = self.env['sales.commission'].search([
            ('sales_person_id', '=', self.sale_person_id.id),
            ('invoice_id', 'in', self.invoice_ids.ids)]).ids
        domain = {'sales_commision_id': [('id', 'in', sales_commisions)]}
        if sales_commisions:
            self.sales_commision_id = sales_commisions[0]
        return {'domain' : domain}

    @api.onchange('sales_commision_id')
    def onchange_sales_commission_id(self):
        for payment in self:
            payment.agent_commision = payment.sales_commision_id.agent_commision or 0.0

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        for payment in self:
            if payment.sales_commision_id or payment.commission_ids:
                if payment.total_amount > payment.amount:
                    raise Warning(_('Total amount is not greater then payment amount.'))
#                 if not payment.agent_commision:
#                     raise Warning(_('Please define marketer commision.'))
#                 amount = (payment.amount * payment.agent_commision) / 100
                
                total_commission = 0.0
                if payment.commission_ids:
                    for line in payment.commission_ids:
                        commission_amount = (line.amount * line.agent_commision) / 100
                        total_commission += commission_amount
                else:
                    if payment.sales_commision_id:
                        total_commission =\
                            (payment.amount * payment.sales_commision_id.agent_commision) / 100
                    
                vals = { 'sales_commission_id': payment.sales_commision_id.id,
                        'amount' : total_commission,
                        'currency_id': payment.currency_id.id,
                        'date': payment.payment_date,
                        'state': 'draft',
#                         'agent_commision': payment.agent_commision,
                        'payment_id': payment.id,
                        'paid_amount': payment.amount,
                        'company_id': payment.company_id.id
                }
                invoice_commision_id = self.env['sales.commission.invoice'].create(vals)
                invoice_id = self.env.context.get('active_id')
                invoice = self.env['account.invoice'].browse(invoice_id)
                invoice.write({'invoice_commision_id': invoice_commision_id.id})
        return res
