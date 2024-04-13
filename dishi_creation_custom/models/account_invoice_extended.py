from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    vendor_bank_details = fields.Text(string='Vendor Bank Details')

    @api.onchange('partner_id')
    def _compute_vendor_bank_details(self):
        for invoice in self:
            bank_details = ""
            if invoice.partner_id and invoice.partner_id.bank_ids:
                # Assuming that 'bank_ids' is a One2many field in 'res.partner' linking to 'res.bank'
                for bank in invoice.partner_id.bank_ids:
                    # Customize this based on your res.bank model structure
                    bank_details += "Bank: {}\nAccount Number: {}\n".format(
                        bank.bank_name, bank.acc_number
                    )
            invoice.vendor_bank_details = bank_details
