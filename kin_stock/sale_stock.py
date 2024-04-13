# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.env['product.uom']._compute_qty_obj(self.product_uom, self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    pass
                    # warning_mess = {
                    #     'title': _('Not enough inventory!'),
                    #     'message' : _('You plan to sell %.2f %s but you only have %.2f %s available!\nThe stock on hand is %.2f %s.') % \
                    #         (self.product_uom_qty, self.product_uom.name, self.product_id.virtual_available, self.product_id.uom_id.name, self.product_id.qty_available, self.product_id.uom_id.name)
                    # }
                    #return {'warning': warning_mess}
        return {}


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    @api.one  # The @api.one calls the methods for as many items in the account.invoice.line, however a for loop can be used inside the method as well to achieve thesame purpose
    @api.depends('selling_price', 'balance')
    def _profit_loss(self):
        self.ensure_one()
        self.profit_loss = self.selling_price + self.balance

    #is_sales_invoice = fields.Boolean(string = "Is Sales Invoice")
    selling_price = fields.Monetary(string="Selling Price")
    profit_loss = fields.Monetary(string="Profit/Loss",compute='_profit_loss',store=True)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

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



class SaleOrderExtend(models.Model):
    _inherit = "sale.order"


    @api.multi
    def action_view_delivery(self):
        res = super(SaleOrderExtend,self).action_view_delivery()
        res['target'] = 'new'
        return  res

