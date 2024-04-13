# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.tools.float_utils import float_compare
from urllib import urlencode
from urlparse import urljoin

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def btn_view_so(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        return {
            'name': _('Sales Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.sale_id])],
            #'context': context,
            # 'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox').id,
            #'res_id': self.env.context.get('cashbox_id'),
            'target': 'new'
        }


    @api.depends('sale_id')
    def _compute_so_count(self):
        for rec in self :
            rec.so_count = len(rec.sale_id)

    @api.multi
    def btn_view_picking(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        return {
            'name': _('Shipments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.picking_id])],
            #'context': context,
            # 'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox').id,
            #'res_id': self.env.context.get('cashbox_id'),
            'target': 'new'
        }

    @api.depends('picking_id')
    def _compute_picking_count(self):
        for rec in self :
            rec.picking_count = len(rec.picking_id)


    @api.multi
    def btn_view_po(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        return {
            'name': _('Purchase Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.purchase_id1])],
            #'context': context,
            # 'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox').id,
            #'res_id': self.env.context.get('cashbox_id'),
            'target': 'new'
        }


    @api.depends('purchase_id1')
    def _compute_po_count(self):
        for rec in self :
            rec.po_count = len(rec.purchase_id1)


    def _get_url(self, module_name,menu_id,action_id, context=None):
        fragment = {}
        res = {}
        model_data = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        fragment['menu_id'] = model_data.get_object_reference(module_name,menu_id)[1]
        fragment['model'] =  'account.invoice'
        fragment['view_type'] = 'form'
        fragment['action']= model_data.get_object_reference(module_name,action_id)[1]
        query = {'db': self.env.cr.dbname}

# for displaying tree view. Remove if you want to display form view
#         fragment['page'] = '0'
#         fragment['limit'] = '80'
#         res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


 # For displaying a single record. Remove if you want to display tree view
        for record in self:
            fragment['id'] =  record.id
            res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


        return res

    # Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line:
            # Load a PO line only once
            if line in self.invoice_line_ids.mapped('purchase_line_id'):
                continue
            if line.product_id.purchase_method == 'purchase':
                qty = line.product_qty - line.qty_invoiced
            else:
                qty = line.qty_received - line.qty_invoiced
            if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
                qty = 0.0
            taxes = line.taxes_id or line.product_id.supplier_taxes_id
            invoice_line_tax_ids = self.purchase_id.fiscal_position_id.map_tax(taxes)
            data = {
                'purchase_line_id': line.id,
                'name': line.name,
                'origin': self.purchase_id.origin,
                'uom_id': line.product_uom.id,
                'product_id': line.product_id.id,
                'account_id': self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
                'price_unit': line.order_id.currency_id.with_context(date=line.order_id.date_order or fields.Date.context_today(self)).compute(line.price_unit, self.currency_id),
                'quantity': qty,
                'discount': 0.0,
                'account_analytic_id': line.account_analytic_id.id,
                'invoice_line_tax_ids': invoice_line_tax_ids.ids,

            }
            account = new_lines.get_invoice_line_account('in_invoice', line.product_id, self.purchase_id.fiscal_position_id, self.env.user.company_id)
            if account:
                data['account_id'] = account.id
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.compute_taxes()
        self.purchase_id = False
        return {}

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            for line in self.invoice_line_ids.filtered(lambda r: r.purchase_line_id):
                line.price_unit = line.purchase_id.currency_id.with_context(date=line.purchase_id.date_order or fields.Date.context_today(self)).compute(line.purchase_line_id.price_unit, self.currency_id)


    @api.model
    def line_get_convert(self, line, part):
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids', []),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uom_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
            'invoice_id': line.get('invoice_id', False),
            'tax_ids': line.get('tax_ids', False),
            'tax_line_id': line.get('tax_line_id', False),
            'selling_price': line.get('selling_price', 0.00),
        }

    @api.model
    def _anglo_saxon_sale_move_lines(self, i_line):
        """Return the additional move lines for sales invoices and refunds.

        i_line: An account.invoice.line object.
        res: The move line entries produced so far by the parent move_line_get.
        """
        inv = i_line.invoice_id
        company_currency = inv.company_id.currency_id.id

        if i_line.product_id.type in ('product', 'consu') and i_line.product_id.valuation == 'real_time':
            fpos = i_line.invoice_id.fiscal_position_id
            accounts = i_line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)
            # debit account dacc will be the output account
            dacc = accounts['stock_output'].id
            # credit account cacc will be the expense account
            cacc = accounts['expense'].id
            if dacc and cacc:
                price_unit = i_line._get_anglo_saxon_price_unit()
                return [
                    {
                        'type':'src',
                        'name': i_line.name[:64],
                        'price_unit': price_unit,
                        'quantity': i_line.quantity,
                        'price': self.env['account.invoice.line']._get_price(inv, company_currency, i_line, price_unit),
                        'account_id':dacc,
                        'product_id':i_line.product_id.id,
                        'uom_id':i_line.uom_id.id,
                        'account_analytic_id': False,
                        'selling_price' : i_line.price_subtotal,
                    },

                    {
                        'type':'src',
                        'name': i_line.name[:64],
                        'price_unit': price_unit,
                        'quantity': i_line.quantity,
                        'price': -1 * self.env['account.invoice.line']._get_price(inv, company_currency, i_line, price_unit),
                        'account_id':cacc,
                        'product_id':i_line.product_id.id,
                        'uom_id':i_line.uom_id.id,
                        'account_analytic_id': False,
                    },
                ]
        return []




    picking_id = fields.Many2one('stock.picking')
    sale_id = fields.Many2one('sale.order')
    picking_count = fields.Integer(compute="_compute_picking_count", string='# of Pickings', copy=False, default=0)
    po_count = fields.Integer(compute="_compute_po_count", string='# of Purchase Orders', copy=False, default=0)
    so_count = fields.Integer(compute="_compute_so_count", string='# of Sales Orders', copy=False, default=0)
    purchase_id1 = fields.Many2one("purchase.order")







class AccountInvoiceLineExtend(models.Model):
    _inherit = "account.invoice.line"


    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLineExtend,self)._onchange_product_id()
        analytic_account_id = self.invoice_id.journal_id.analytic_account_id

        if analytic_account_id :
            self.account_analytic_id = analytic_account_id



        return res





    def _set_additional_fields(self, invoice):
        """ Some modules, such as Purchase, provide a feature to add automatically pre-filled
            invoice lines. However, these modules might not be aware of extra fields which are
            added by extensions of the accounting module.
            This method is intended to be overridden by these extensions, so that any new field can
            easily be auto-filled as well.
            :param invoice : account.invoice corresponding record
            :rtype line : account.invoice.line record
        """
        res =  super(AccountInvoiceLineExtend,self)._set_additional_fields(invoice)

        analytic_account_id = invoice.journal_id.analytic_account_id or False

        if analytic_account_id :
            self.account_analytic_id = analytic_account_id


        return  res