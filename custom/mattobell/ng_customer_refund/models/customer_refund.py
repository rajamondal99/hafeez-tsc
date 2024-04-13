# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError


class CustomerRefundRequest(models.Model):
    _name = 'customer.refund.request'
    _description = 'Customer Refund Request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    name = fields.Char(string='Name', default="/", readonly=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirmed'),
                                        ('approved', 'Approved'),
                                        ('refund_invoiced', 'Refund Awaiting Payment'),
                                        ('cancel', 'Cancelled'),
                                        ('reject', 'Rejected')],
                                string='State',
                                readonly=True,
                                default='draft',
                                track_visibility='onchange')
    product_template_id = fields.Many2one('product.template', 
                                          string='Estate',
                                          required=True,
                                          readonly=True,
                                          states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product',
                                 string='Plot Size',
                                 required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]})
    surcharge = fields.Float(string='Surcharge (%)',
                             readonly=True,
                             states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner',
                                 string='Customer',
                                 required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]})
    customer_account_id = fields.Many2one('sale.property.reference',
                                          string='Property Reference',
                                          required=True,
                                          readonly=True,
                                          states={'draft': [('readonly', False)]})
    full_initial_amount = fields.Float(string='Full Intial Amount',
                                       compute="_compute_amount_paid",
                                       store=True,)
    amount_paid_to_date = fields.Float(string='Amount Paid To Date',
                                       compute="_compute_amount_paid",
                                       store=True,)
    balance = fields.Float(string='Balance',
                           compute="_compute_amount_paid",
                           store=True,)
    refund_amount = fields.Float(compute="_compute_refund_amount",
                                 string='Refundable Amount',
                                 store=True,)
    journal_id = fields.Many2one('account.journal',
                                 string='Journal')
    user_id = fields.Many2one('res.users',
                              default=lambda self: self.env.user,
                              string='Responsible User',
                              readonly=True,
                              states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id,
                                 string='Company',
                                 readonly=True,
                                )
    request_date = fields.Date(string='Request Date',
                               readonly=True,
                               states={'draft': [('readonly', False)]},
                               default=fields.Date.context_today)
    note = fields.Text(string='Notes', )
    
    confirm_date = fields.Date(string='Confirmed Date',
                        readonly=True, copy=False)
    approved_date = fields.Date(string='Approved Date',
                        readonly=True, copy=False)
    refund_invoiced_date = fields.Date(string='Refund Invoiced Date',
                        readonly=True, copy=False)
    paid_date = fields.Date(string='Paid Date',
                        readonly=True, copy=False)
    
    confirm_by_id = fields.Many2one('res.users',
                                    string='Confirm By',
                                    readonly=True,
                                    copy=False)
    approved_by_id = fields.Many2one('res.users',
                                     string='Approved By',
                                     readonly=True,
                                     copy=False)
    refund_invoiced_by_id = fields.Many2one('res.users',
                                            string='Refund Invoiced By',
                                            readonly=True,
                                            copy=False)
    paid_by_id = fields.Many2one('res.users',
                                 string='Paid By',
                                 readonly=True,
                                 copy=False)
    currency_id = fields.Many2one('res.currency',
                                  string="Currency",
                                  readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.company_id.currency_id,)
    invoice_id = fields.Many2one('account.invoice',
                                 string="Refund Ref",
                                 readonly=True)
    refund_state = fields.Selection(related="invoice_id.state",
                                    string="Refund Status",
                                    readonly=True)

    @api.depends('customer_account_id', 'note')
    def _compute_amount_paid(self):
        for refund in self:
            if refund.customer_account_id and refund.customer_account_id.sale_line_id:
                sale_line = refund.customer_account_id.sale_line_id
                sale_order = sale_line.order_id
                amount_paid = 0.0
                if sale_order.use_installment_invoice:
                    refund.full_initial_amount = sale_line.price_subtotal_property
                else:
                    refund.full_initial_amount = sale_line.price_subtotal
                for invoice_line in sale_line.invoice_lines:
                    invoice = invoice_line.invoice_id
                    if sale_order.use_installment_invoice:
                        if invoice.use_installment_invoice:
                            if invoice.state == 'paid':
                                amount_paid += invoice.amount_total
                    else:
                        if not invoice.use_installment_invoice:
                            for payment in invoice.payment_ids:
                                amount_paid += payment.amount
#                             if invoice.state == 'paid':
#                                 amount_paid += invoice.amount_total
                refund.amount_paid_to_date = amount_paid
                refund.balance = refund.full_initial_amount - amount_paid

    @api.onchange('customer_account_id')
    def onchange_customer_account_id(self):
        for refund in self:
            refund.currency_id = refund.customer_account_id.sale_line_id.currency_id.id
        
    @api.onchange('product_id')
    def onchange_surcharge(self):
        for refund in self:
            refund.surcharge = refund.product_id.surcharge

    @api.depends('amount_paid_to_date', 'surcharge')
    def _compute_refund_amount(self):
        for refund in self:
            if refund.amount_paid_to_date and refund.surcharge:
                charged_amount = (refund.amount_paid_to_date * refund.surcharge) / 100
                refund.refund_amount = refund.amount_paid_to_date - charged_amount

    @api.multi
    def action_confirm(self):
        for refund in self:
            refund.state = 'confirm'
            refund.confirm_date = fields.Date.today()
            refund.confirm_by_id = self.env.user.id
            refund.name = self.env['ir.sequence'].next_by_code('customer.refund.request')

    @api.multi
    def action_approved(self):
        for refund in self:
            refund.state = 'approved'
            refund.approved_date = fields.Date.today()
            refund.approved_by_id = self.env.user.id

    @api.multi
    def action_create_refund_invoice(self):
        for refund in self:
            if refund.refund_amount == 0.0:
                raise UserError(_('You can not create refund with zero amount.'))
            account = refund.product_id.property_account_income_id or refund.product_id.categ_id.property_account_income_categ_id
            invoice_vals = {
                'name': refund.name,
                'origin': refund.name,
                'type': 'out_refund',
                'account_id': refund.partner_id.property_account_receivable_id.id,
                'partner_id': refund.partner_id.id,
                'journal_id': refund.journal_id.id,
                'currency_id': refund.currency_id.id,
                'payment_term_id': refund.partner_id.property_payment_term_id.id,
                'fiscal_position_id': refund.partner_id.property_account_position_id.id,
                'company_id': refund.company_id.id,
                'user_id': refund.user_id and refund.user_id.id,
            }
            invoice_id = self.env['account.invoice'].create(invoice_vals)
            invoice_line_vals = {
                'name': refund.name,
                'origin': refund.name,
                'account_id': account.id,
                'price_unit': refund.refund_amount,
                'quantity': 1,
                'uom_id': refund.product_id.uom_id.id,
                'product_id': refund.product_id.id or False,
                'invoice_line_tax_ids': [(6, 0, refund.customer_account_id.sale_line_id.tax_id.ids)],
                'invoice_id': invoice_id.id,
                'preoperty_ref_id': refund.customer_account_id.id,
            }
            self.env['account.invoice.line'].create(invoice_line_vals)
            refund.invoice_id = invoice_id.id
            refund.state = 'refund_invoiced'
            refund.refund_invoiced_date = fields.Date.today()
            refund.refund_invoiced_by_id = self.env.user.id

    @api.multi
    def action_paid(self):
        for refund in self:
            refund.state = 'paid'
            refund.paid_date = fields.Date.today()
            refund.paid_by_id = self.env.user.id

    @api.multi
    def action_cancel(self):
        for refund in self:
            refund.state = 'cancel'

    @api.multi
    def action_reject(self):
        for refund in self:
            refund.state = 'reject'

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
