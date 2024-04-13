from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    clearing_account_id = fields.Many2one('account.account',
                                          'Clearing Account')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    agent_id = fields.Many2one('sales.agent', string='Marketer')
    sale_installment_id = fields.Many2one('sale.order', string='Installment Sales')
    use_installment_invoice = fields.Boolean('Use Installment Invoice')
    clearing_move_id = fields.Many2one('account.move', 'Clearing Move', readonly=True)

    @api.multi
    def action_move_create(self):
        for inv in self:
            company = inv.company_id
            account_move = self.env['account.move']
            if inv.use_installment_invoice:
                if not company.clearing_account_id:
                    raise Warning(_('Please define clearing account on company.'))
                if not inv.journal_id.sequence_id:
                    raise UserError(_('Please define sequence on the journal related to this invoice.'))
                if not inv.invoice_line_ids:
                    raise UserError(_('Please create some invoice lines.'))
                if inv.move_id:
                    continue
                clearing_account_id = company.clearing_account_id.id
                
                company_currency = inv.company_id.currency_id
                ctx = self._context.copy()
                ctx.update(lang=inv.partner_id.lang)
                if not inv.date_invoice:
                    inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
                date_invoice = inv.date_invoice
                ctx['date'] = date_invoice
                journal = inv.journal_id.with_context(ctx)
                name = inv.name or '/'
                move_vals = {
                    'date' : date_invoice,
                    'ref' : inv.number or '',
                    'journal_id': journal.id,
                    'name' :  name,
                    'partner_id': inv.partner_id.id,
                }
                
                move_id = self.env['account.move'].create(move_vals)
                inv.write({'clearing_move_id': move_id.id})
                diff_currency = inv.currency_id != company_currency
                if inv.currency_id != company_currency:
                    amount_currency = company_currency.with_context(ctx).compute(inv.amount_total, inv.currency_id)
                else:
                    amount_currency = False
                sign = journal.type == 'purchase' and 1 or -1
                if inv.amount_total > 0.0:
                    move_line_vals = []
                    move_line_vals.append((0,0, {
                        'name':name,
                        'debit': 0.0,
                        'credit': inv.amount_total,
                        'account_id': clearing_account_id,
                        'move_id': move_id.id,
                        'journal_id': journal.id,
                        'partner_id': False,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'amount_currency': diff_currency and amount_currency,
                        'date': date_invoice,
                        'analytic_account_id': False,
                    }))
                    move_line_vals.append((0,0,{
                        'name': name,
                        'debit': inv.amount_total,
                        'credit': 0.0,
                        'account_id': clearing_account_id,
                        'move_id': move_id.id,
                        'journal_id': journal.id,
                        'partner_id': False,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'amount_currency':  diff_currency and amount_currency,
                        'date': date_invoice,
                    }))
                    move_id.write({'line_ids': move_line_vals})
                return True
        return super(AccountInvoice, self).action_move_create()

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"
    
    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if order.agent_id:
            res.agent_id = order.agent_id.id
        return res
    
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    @api.depends('product_uom_qty', 'discount', 'base_sale_price', 'tax_id')
    def _compute_property_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.base_sale_price * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax_property': taxes['total_included'] - taxes['total_excluded'],
                'price_total_property': taxes['total_included'],
                'price_subtotal_property': taxes['total_excluded'],
            })
    
    @api.depends('installment_number')
    def _compute_done_installment(self):
        for line in self:
            if line.installment_number == 0:
                line.done_installment = True
    
    base_sale_price = fields.Float('Base Sale Price')
    price_subtotal_property = fields.Monetary(compute='_compute_property_amount', string='Subtotal Property', readonly=True, store=True)
    price_tax_property = fields.Monetary(compute='_compute_property_amount', string='Taxes Property', readonly=True, store=True)
    price_total_property = fields.Monetary(compute='_compute_property_amount', string='Total Property', readonly=True, store=True)
    installment_number = fields.Integer('Number of Installment',copy=False, default=1)
    done_installment = fields.Boolean(compute='_compute_done_installment',
        string="Complete Installment", store=True,copy=False)
    price_unit_installment = fields.Float('Price Unit Installment')
    
    
    @api.onchange('property_installment_id',
                  'installment_number',
                  'property_installment_id.total_number_installment')
    def onchange_property_installment(self):
        for rec in self:
            rec.base_sale_price = rec.property_installment_id.total_sale_price
            rec.installment_number = rec.property_installment_id.total_number_installment
            rec.agent_commision = rec.property_installment_id.agent_commision
            if rec.property_installment_id.total_number_installment > 0:
#                 rec.price_unit = rec.base_sale_price / rec.property_installment_id.total_number_installment
                rec.price_unit_installment = rec.base_sale_price / rec.property_installment_id.total_number_installment

    @api.onchange('base_sale_price')
    def onchange_base_sale_price(self):
        for rec in self:
            if rec.base_sale_price and rec.property_installment_id.total_number_installment > 0:
                rec.price_unit = rec.base_sale_price
#                 rec.price_unit = rec.base_sale_price / rec.property_installment_id.total_number_installment
                rec.price_unit_installment = rec.base_sale_price / rec.property_installment_id.total_number_installment
    
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.depends('order_line.price_total_property')
    def _property_amount_all(self):
        """
        Compute the total property amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal_property
                amount_tax += line.price_tax_property
            order.update({
                'amount_untaxed_property': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax_property': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total_property': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.installment_number', 'installment_invoice_ids')
    def _compute_all_done_installment(self):
        for order in self:
            order.is_done_all_installments = True
            for line in order.order_line:
                if not line.done_installment:
                    order.is_done_all_installments = False
    
    amount_untaxed_property = fields.Monetary(string='Untaxed Amount Property', store=True, readonly=True, compute='_property_amount_all', track_visibility='always')
    amount_tax_property = fields.Monetary(string='Property Taxes', store=True, readonly=True, compute='_property_amount_all', track_visibility='always')
    amount_total_property = fields.Monetary(string='Property Total', store=True, readonly=True, compute='_property_amount_all', track_visibility='always')
    installment_invoice_ids = fields.One2many('account.invoice', 'sale_installment_id', 'Installment Invoices',copy=False)
    is_done_all_installments = fields.Boolean(compute='_compute_all_done_installment',
        string="All Installment done",
        store=True,
        copy=False)
    create_automatic_installment_invoice = fields.Boolean('Create Installment Invoice Automatic?',
                                                          readonly=True,
                                                          states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    use_installment_invoice = fields.Boolean('Use Installment Invoice', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'agent_id' : self.agent_id and self.agent_id.id or False,})
        return res

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        sale_ids = self._context.get('active_ids', [])
        for order in self.browse(sale_ids):
            if order.invoice_ids:
                raise UserError(_('Sorry. Invoices already created.'))
        res = super(SaleOrder, self).action_invoice_create(grouped=grouped, final=final)
        for order in self.browse(sale_ids):
            if order.use_installment_invoice:
                while order.is_done_all_installments is False:
                    order.create_installment_invoices()
        return res
    
    
    @api.multi
    def create_installment_invoices(self):
        for order in self:
            inv_data = order._prepare_invoice()
            inv_data.update({'sale_installment_id': order.id,
                             'use_installment_invoice': self.use_installment_invoice})
            invoice = self.env['account.invoice'].create(inv_data)
            for line in order.order_line:
                if not line.done_installment:
                    line_vals = line._prepare_invoice_line(qty=line.product_uom_qty)
                    line_vals['price_unit'] = line.price_unit_installment
                    line_vals.update({'invoice_id': invoice.id, 'sale_line_ids': [(6, 0, [line.id])]})
                    inv_line = self.env['account.invoice.line'].create(line_vals)
                    line.installment_number = line.installment_number - 1


#     @api.multi
#     def create_installment_invoices(self):
#         for order in self:
#             inv_data = order._prepare_invoice()
#             inv_data.update({'sale_installment_id': order.id})
#             invoice = self.env['account.invoice'].create(inv_data)
#             for line in order.order_line:
#                 if not line.done_installment:
#                     line_vals = line._prepare_invoice_line(qty=line.product_uom_qty)
#                     line_vals.update({'invoice_id': invoice.id, 'sale_line_ids': [(6, 0, [line.id])]})
#                     inv_line = self.env['account.invoice.line'].create(line_vals)
#                     line.installment_number = line.installment_number - 1

    @api.model
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        context = self.env.context.copy()
        if 'installment_id' in kwargs:
            installment_id = kwargs.get('installment_id')
            if not int(installment_id) == 0:
                context.update({'installment_id': kwargs.get('installment_id')})
        elif line_id:
            order_line = self.env['sale.order.line'].browse(line_id)
            if order_line.property_installment_id:
                installment_id = order_line.property_installment_id
                context.update({'installment_id': installment_id.id})
        result = super(SaleOrder, self.with_context(context))._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        if kwargs and kwargs.get('installment_id', False):
            line = result.get('line_id')
            installment_id = kwargs.get('installment_id')
            installment = self.env['product.installment.config'].browse(int(installment_id))
            order_line = self.env['sale.order.line'].browse(line)
            order_line.write({'property_installment_id': installment.id})
        return result
    
    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0):
        res = super(SaleOrder, self)._website_product_id_change(order_id, product_id, qty)
        if 'installment_id' in self.env.context:
            installment_id = self.env.context.get('installment_id')
            installment = self.env['product.installment.config'].browse(int(installment_id))
            res.update(price_unit = installment.monthly_installment,
                       base_sale_price = installment.total_sale_price,
                       installment_number = installment.total_number_installment)
        return res
