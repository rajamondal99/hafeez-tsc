from openerp import models, fields,api
from datetime import datetime
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from urllib import urlencode
from urlparse import urljoin



class AccountExtend(models.Model):
    _inherit = 'account.invoice'

    sale_order_id = fields.Many2one('sale.order',string="SO reference")

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        #account timeout update
        purchase_obj = self.env['purchase.order'].search([['id','=',self.purchase_id.id]])
        if purchase_obj.state =='purchase':
            purchase_obj.update({'finance_vendor_bill_created':True})

        self.sale_order_id = self.purchase_id.sale_order_id.id
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
		'sale_order_id':self.purchase_id.sale_order_id.id,
                'uom_id': line.product_uom.id,
                'product_id': line.product_id.id,
                'account_id': self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
                'price_unit': line.order_id.currency_id.with_context(date=line.order_id.date_order or fields.Date.context_today(self)).compute(line.price_unit, self.currency_id),
                'quantity': qty,
                'discount': line.discount,
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
        self.purchase_id = False
        return {}

