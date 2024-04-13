# -*- coding: utf-8 -*-
from openerp import api, fields, models, _


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    
    email_cc = fields.Many2many('res.partner', 'mailcompose_partnercc_rel','mailid','partner_id', string="Cc", help='Carbon copy message recipients')
    email_bcc = fields.Many2many('res.partner', 'mailcompose_partnerbcc_rel','mailid','partner_id', string="Bcc", help='Blind Carbon copy message recipients')
    

    @api.model
    def default_get(self, fields):
        result = super(MailComposer, self).default_get(fields)
        if result.get('model', False):
            follower_ids = self.env['document.followers'].search([('model_id.model','=',result.get('model')),('auto_add_followers','=',True)])
            result['email_cc'] = [(4, user.partner_id.id) for user in follower_ids.internal_follower_ids]
            result['email_bcc'] = [(4, user.partner_id.id) for user in follower_ids.external_follower_ids]
        return result

    @api.multi
    def get_mail_values(self, res_ids):
        """Generate the values that will be used by send_mail to create mail_messages
        or mail_mails. """
        self.ensure_one()
        results = dict.fromkeys(res_ids, False)
        rendered_values = {}
        mass_mail_mode = self.composition_mode == 'mass_mail'

        # render all template-based value at once
        if mass_mail_mode and self.model:
            rendered_values = self.render_message(res_ids)
        # compute alias-based reply-to in batch
        reply_to_value = dict.fromkeys(res_ids, None)
        if mass_mail_mode and not self.no_auto_thread:
            # reply_to_value = self.env['mail.thread'].with_context(thread_model=self.model).browse(res_ids).message_get_reply_to(default=self.email_from)
            reply_to_value = self.env['mail.thread'].with_context(thread_model=self.model).message_get_reply_to(res_ids, default=self.email_from)
        
        for res_id in res_ids:
            # static wizard (mail.message) values
            mail_values = {
                'subject': self.subject,
                'body': self.body or '',
                'parent_id': self.parent_id and self.parent_id.id,
                'partner_ids': [partner.id for partner in self.partner_ids],
                'email_partner_cc': [(4, partner.id) for partner in self.email_cc],
                'email_partner_bcc': [(4, partner.id) for partner in self.email_bcc],
                'attachment_ids': [attach.id for attach in self.attachment_ids],
                'author_id': self.author_id.id,
                'email_from': self.email_from,
                'record_name': self.record_name,
                'no_auto_thread': self.no_auto_thread,
                'mail_server_id': self.mail_server_id.id,
            }
            # mass mailing: rendering override wizard static values
            if mass_mail_mode and self.model:
                # always keep a copy, reset record name (avoid browsing records)
                mail_values.update(notification=True, model=self.model, res_id=res_id, record_name=False)
                # auto deletion of mail_mail
                if self.template_id and self.template_id.auto_delete:
                    mail_values['auto_delete'] = True
                # rendered values using template
                email_dict = rendered_values[res_id]
                mail_values['partner_ids'] += email_dict.pop('partner_ids', [])
                mail_values.update(email_dict)
                if not self.no_auto_thread:
                    mail_values.pop('reply_to')
                    if reply_to_value.get(res_id):
                        mail_values['reply_to'] = reply_to_value[res_id]
                if self.no_auto_thread and not mail_values.get('reply_to'):
                    mail_values['reply_to'] = mail_values['email_from']
                # mail_mail values: body -> body_html, partner_ids -> recipient_ids
                mail_values['body_html'] = mail_values.get('body', '')
                mail_values['recipient_ids'] = [(4, id) for id in mail_values.pop('partner_ids', [])]

                # process attachments: should not be encoded before being processed by message_post / mail_mail create
                mail_values['attachments'] = [(name, base64.b64decode(enc_cont)) for name, enc_cont in email_dict.pop('attachments', list())]
                attachment_ids = []
                for attach_id in mail_values.pop('attachment_ids'):
                    new_attach_id = self.env['ir.attachment'].browse(attach_id).copy({'res_model': self._name, 'res_id': self.id})
                    attachment_ids.append(new_attach_id.id)
                mail_values['attachment_ids'] = self.env['mail.thread']._message_preprocess_attachments(
                    mail_values.pop('attachments', []),
                    attachment_ids, 'mail.message', 0)

            results[res_id] = mail_values
        return results