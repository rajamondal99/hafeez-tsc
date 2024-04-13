# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html


from openerp import api, fields, models, _
from datetime import datetime, timedelta, date
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError
from urllib import urlencode
from urlparse import urljoin

class sla(models.Model):
    _name = "kin.sla"
    _description = "Service Level Agreement"

    name = fields.Char(string='SLA Policy Name')
    helpdesk_team_id = fields.Many2one(string='Help Desk Team')

class HelpDesk(models.Model):
    _name = "kin.helpdesk.team"
    _description = "Help Desk"

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Help Desk Name already exists !"),
    ]

class TicketCategory(models.Model):
    _name = "kin.ticket.category"
    _description = "Tags for Tickets"

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class TicketCost(models.Model):
    _name = 'kin.ticket.cost'

    @api.model
    def create(self, vals):

        analytic_line_obj = self.env['account.analytic.line']
        ticket_obj = self.env['kin.ticket']

        analytic_account_id = vals.get('analytic_account_id',False)
        ticket_id = vals.get('ticket_id',False)
        ticket_cost = vals.get('ticket_cost',False)

        if analytic_account_id and ticket_id and ticket_cost:
            ticket = ticket_obj.browse(ticket_id)
            ticket_name = ticket.name
            ticket_id = ticket.ticket_id
            data = {
                'name' : ticket_name + ' - ' + ticket_id  ,
                'account_id' : analytic_account_id ,
                'amount' : ticket_cost,
            }
            line_id = analytic_line_obj.create(data)
            ticket.analytic_line_id = line_id.id

        res = super(TicketCost, self).create(vals)
        res.analytic_line_id = line_id.id
        return res

    @api.multi
    def write(self, vals):
        ticket_cost = vals.get('ticket_cost', False)
        line = self.analytic_line_id or False
        if ticket_cost and line:
            self.analytic_line_id.amount = ticket_cost

        res = super(TicketCost, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            rec.analytic_line_id.unlink()
        return super(TicketCost, self).unlink()

    # @api.model
    # def _default_user(self):
    #     return self.env.context.get('user_id', self.env.user.id)

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost/Analytic Account.')
    analytic_line_id = fields.Many2one('account.analytic.line',string='Analytic Line')
    ticket_cost = fields.Monetary(string='Cost')
    ticket_id = fields.Many2one('kin.ticket',string='Ticket',ondelete='cascade')
    # user_id = fields.Many2one('res.users', string='User', default=_default_user)
    # company_id = fields.Many2one(related='user_id.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one( string="Currency",  default=lambda self: self.env.user.company_id.currency_id.id)


class Ticket(models.Model):
    _name = 'kin.ticket'
    _description = "Help Desk Ticket"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_url(self, module_name, menu_id, action_id, context=None):
        fragment = {}
        res = {}
        model_data = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        fragment['menu_id'] = model_data.get_object_reference(module_name, menu_id)[1]
        fragment['model'] = 'kin.ticket'
        fragment['view_type'] = 'form'
        fragment['action'] = model_data.get_object_reference(module_name, action_id)[1]
        query = {'db': self.env.cr.dbname}
        # for displaying tree view. Remove if you want to display form view
        #         fragment['page'] = '0'
        #         fragment['limit'] = '80'
        #         res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


        # For displaying a single record. Remove if you want to display tree view
        fragment['id'] = context.get("ticket_id")
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res

    # @api.multi
    # def write(self,vals):
    #     engineer_ids = vals.get('engineer_ids',False)
    #     if engineer_ids :
    #         the_engineer_ids = engineer_ids[0][0][2]
    #         #Send email to all engineers
    #         company_email = self.env.user.company_id.email.strip()
    #         support_person_email = self.env.user.partner_id.email.strip()
    #         support_person_name = self.env.user.name
    #
    #         if company_email and support_person_email:
    #             # Custom Email Template
    #             mail_template = self.env.ref('kin_helpdesk.mail_templ_assign_engineer_email')
    #             ctx = {}
    #             ctx.update({'ticket_id': self.id})
    #             the_url = self._get_url('product', 'menu_helpdesk_all_tickets', 'action_view_all_tickets', ctx)
    #
    #             user_ids = []
    #             for user in engineer_ids:
    #                 if user.partner_id.email and user.partner_id.email.strip():
    #                     user_ids.append(user.id)
    #                     ctx = {'system_email': company_email,
    #                            'support_person_name': support_person_name,
    #                            'support_person_email': support_person_email,
    #                            'notify_person_email': user.partner_id.email,
    #                            'notify_person_name': user.partner_id.name,
    #                            'url': the_url,
    #                            }
    #                     mail_template.with_context(ctx).send_mail(self.id, force_send=False)
    #
    #     res = super(Ticket,self).write(vals)

    @api.multi
    def btn_ticket_open(self):
        self.state = 'new'
        self.open_date = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.message_post( _('A new Ticket with Ticket ID %s has been opened for the issue (%s)') % (self.ticket_id,self.name),subject='A new ticket with ID %s has been opened' % (self.ticket_id), subtype='mail.mt_comment')


    @api.multi
    def btn_ticket_progress(self):
        self.state = 'progress'


    @api.multi
    def btn_ticket_done(self):
        self.state = 'done'
        self.message_post( _('The Ticket with Ticket ID %s has been resolved for the issue (%s)') % (self.ticket_id,self.name),subject='The issue for the ticket with ID %s  has been resolved' % (self.ticket_id), subtype='mail.mt_comment')



    @api.multi
    def btn_ticket_close(self):
        self.state = 'closed'
        self.closed_date = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self._compute_time_spent()
        self.message_post( _('The Ticket with Ticket ID %s has been closed for the issue (%s)') % (self.ticket_id,self.name),subject='The ticket with ID %s  has been closed' % (self.ticket_id), subtype='mail.mt_comment')


    @api.multi
    def btn_ticket_reset(self):
        self.state = 'draft'
        self.open_date = self.closed_date = self.time_spent = False


    @api.multi
    def read(self, fields=None, load='_classic_read'):
        res =  super(Ticket, self).read(fields=fields, load=load)
        self._compute_time_elapsed()
        return res


    @api.multi
    def unlink(self):
        for ticket in self:
            if ticket.state not in 'draft':
                raise UserError(_("Cannot delete ticket that is not in draft state."))
            ticket.ticket_cost_ids.unlink()
        return super(Ticket, self).unlink()


    @api.model
    def create(self,vals):
        vals['ticket_id'] = self.env['ir.sequence'].get('tick_id_code')
        vals['assigned_date'] = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        ticket_obj = super(Ticket,self).create(vals)
        if vals.get('partner_id',False)  :
            user_ids = []
            partner_ids = []
            partner_ids.append(ticket_obj.partner_id.id)
            ticket_obj.message_subscribe(partner_ids=partner_ids)
            #ticket_obj.message_subscribe_users(user_ids=user_ids)
            #inv_obj.message_post( _('A New Ticket has been Opened with Ticket No: %s.') % (ticket_obj.ticket_id),subject='A New Ticket ahs been created for your request', subtype='mail.mt_comment')

        return ticket_obj

    def _compute_time_spent(self):
        for ticket in self :
            if  ticket.open_date and ticket.closed_date :
                closed_date = datetime.strptime(ticket.closed_date, DEFAULT_SERVER_DATETIME_FORMAT)
                open_date = datetime.strptime(ticket.open_date , DEFAULT_SERVER_DATETIME_FORMAT)
                date_diff =  str(closed_date - open_date)
                ticket.time_spent = date_diff

    def _compute_time_elapsed(self):
        for ticket in self :
            if  ticket.open_date and not ticket.closed_date :
                today_date = datetime.strptime(datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)
                open_date = datetime.strptime(ticket.open_date , DEFAULT_SERVER_DATETIME_FORMAT)
                date_diff =  str(today_date - open_date)
                ticket.time_elapsed = date_diff

    def _compute_duration(self):
        for ticket in self :
            if ticket.expected_finish_date and ticket.assigned_date :
                expected_finish_date = datetime.strptime(ticket.expected_finish_date , DEFAULT_SERVER_DATETIME_FORMAT)
                assigned_date = datetime.strptime(ticket.assigned_date , DEFAULT_SERVER_DATETIME_FORMAT)
                date_diff =  str(expected_finish_date - assigned_date)
                ticket.duration =  date_diff

    name = fields.Char(string="Subject",required=1, default='New Ticket')
    partner_id = fields.Many2one('res.partner',string='Customer')
    partner_name = fields.Char( string="Customer's Name")
    email = fields.Char(string ='Email')
    mobile = fields.Char(string ='Mobile')
    phone = fields.Char(string ='Phone')
    description = fields.Html(string='Description')
    assigned_date = fields.Datetime(string='Assigned Date')
    open_date = fields.Datetime(string='Open Ticket Date')
    closed_date = fields.Datetime(string='Closed Ticket Date')
    time_elapsed = fields.Char(string='Time Elapsed',readonly=1)
    time_spent = fields.Char(string='Time Spent to Close Ticket',readonly=1)
    expected_finish_date = fields.Datetime(string='Expected Finished Date')
    duration = fields.Char(string='Duration(days)',compute='_compute_duration') #Do not set store parameter for compute fields, other wise it will not show any value
    priority = fields.Selection([('0','low'), ('1','Medium'),('2','High'),('3','Critical')], default=0, string='Priority', select=True, store=True)
    attachment = fields.Binary(string='Attachment',  attachment=True)
    ticket_id = fields.Char(string='Ticket ID')
    user_id = fields.Many2one('res.users',string='Support Person',default=lambda self: self.env.user.id)
    category_ids = fields.Many2many('kin.ticket.category',string='Ticket Category')
    ticket_type = fields.Selection([('issue','Issue'), ('question','Question')], string='Ticket Type', select=True)
    engineer_ids = fields.Many2many('res.users',string='Engineers')
    ticket_cost_ids = fields.One2many('kin.ticket.cost','ticket_id',string='Costs')
    state = fields.Selection([('draft','Draft'),('new','Open'),('progress','In Progress'), ('done','Resolved'),('closed','Closed')],default='draft', track_visibility='onchange')




