# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_invoice_payment_sent(self):
        """ Open a window to compose an email, with the edi payment receipt template
            message loaded by default
        """
        if not self.payment_ids:
            raise Warning(_('There are no payment(s) found for this invoice!'))
        
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        template = self.env.ref('invoice_payment_receipt.email_template_edi_invoice_payment', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model = 'account.invoice',
            default_res_id  = self.id,
            default_use_template = bool(template),
            default_template_id = template.id,
            default_composition_mode = 'comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        
    @api.multi
    def confirm_paid(self):
        res = super(account_invoice, self).confirm_paid()
        if self.partner_id.send_invoice_payment_receipt:
            template = self.env.ref('invoice_payment_receipt.email_template_edi_invoice_payment', False)
            template.send_mail(self.id)
        return res

class Customer(models.Model):
    _inherit = "res.partner"
    
    send_invoice_payment_receipt = fields.Boolean(string='Send Invoice Payment Receipt ?', default=False, help="Tick this box if you want to send email notification to customer when invoice will be paid.")
    
#                 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
