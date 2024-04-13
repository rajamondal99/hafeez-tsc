# -*- coding: utf-8 -*-

from openerp import fields, models, api, _

class account_payment(models.Model):
    _name = 'account.payment'
    _inherit = ['mail.thread', 'account.payment']

    @api.multi
    def post(self):
        res = super(account_payment, self).post()
        if self.partner_id.send_payment_order and self.payment_type == 'inbound':
            try:
                template_id = self.env['ir.model.data'].get_object_reference('account_payment_report', 'email_template_edi_payment_order')[1]
            except ValueError:
                template_id = False
            if template_id:
                template_data = self.env['mail.template'].browse(template_id)
                ctx = self.env.context.copy()
                if ctx.get('active_model') == 'account.invoice':
                    ctx['active_model'] = 'account.payment'
                    ctx['active_ids'] = self.ids
                    ctx['active_id'] = self.ids[0]
                msg_id = template_data.with_context(ctx).send_mail(self.ids[0])
        return res
