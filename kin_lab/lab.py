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


class KinClient(models.Model):
    _name = 'kin.client'

    name = fields.Char(string='Consultant', placholder="Consultant's Name")
    client_id = fields.Char(string='Client Number')
    address = fields.Text(string='Address')
    phone = fields.Integer(string='Phone')
    mobile = fields.Integer(string='Mobile')
    email = fields.Char(string='Email')
    note = fields.Text(string='Notes')
    age = fields.Integer(string='Age')
    sex = fields.Selection([('male','Male'), ('female','Female')], string='Sex', select=True)


class KinLabDocument(models.Model):
    _name = 'kin.lab.document'

    name = fields.Char(string='Lab Document')
    referring_id = fields.Many2one('kin.referral',string='Referral')
    state = fields.Selection(
        [('draft', 'Draft'), ('new', 'Open'), ('progress', 'In Progress'), ('done', 'Resolved'), ('closed', 'Closed')],
        default='draft', track_visibility='onchange')


class KinProfessional(models.Model):
    _name = 'kin.professionals'

    name = fields.Char(string='Consultant',placholder="Consultant's Name")
    speciality_id = fields.Many2one('kin.medical.specialization',string='Specialization')
    verified = fields.Boolean('Verified')
    address = fields.Text(string='Address')
    phone = fields.Integer(string='Phone')
    mobile = fields.Integer(string='Mobile')
    email = fields.Char(string='Email')
    note = fields.Text(string='Notes')



class KinUnits(models.Model):
    _name = 'kin.units'

    name = fields.Char(string='Unit')
    description = fields.Text(string='Description')

class KinMedicalSpecialization(models.Model):
    _name = 'kin.medical.specialization'

    id = fields.Char(string='ID')
    spaciality = fields.Char(string='Speciality')

class KinReferral(models.Model):
    _name = 'kin.referral'

    name = fields.Char(string='Name')
    address = fields.Text(string='Address')
    phone = fields.Integer(string='Phone')
    mobile = fields.Integer(string='Mobile')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')


class KinLab(models.Model):
    _name = 'kin.lab'

    name = fields.Char(string="Subject",required=1, default='New Ticket')
    partner_id = fields.Many2one('res.partner',string='Customer')
    email = fields.Char(related='partner_id.email',string ='Email')
    mobile = fields.Char(related='partner_id.mobile',string ='Mobile')
    phone = fields.Char(related='partner_id.phone',string ='Phone')
    description = fields.Html(string='Description')
    assigned_date = fields.Datetime(string='Assigned Date')
    open_date = fields.Datetime(string='Open Ticket Date')
    closed_date = fields.Datetime(string='Closed Ticket Date')
    time_elapsed = fields.Char(string='Time Elapsed',readonly=1)
    time_spent = fields.Char(string='Time Spent to Close Ticket',readonly=1)
    expected_finish_date = fields.Datetime(string='Expected Finished Date')
    duration = fields.Char(string='Duration(days)',compute='_compute_duration') #Do not set store parameter for compute fields, other wise it will not show any value
    priority = fields.Selection([('0','low'), ('1','Medium'),('1','High'),('2','Critical')], default=0, string='Priority', select=True)
    attachment = fields.Binary(string='Attachment',  attachment=True)
    ticket_id = fields.Char(string='Ticket ID')
    user_id = fields.Many2one('res.users',string='Support Person',default=lambda self: self.env.user.id)
    category_ids = fields.Many2many('kin.ticket.category',string='Ticket Category')
    ticket_type = fields.Selection([('issue','Issue'), ('question','Question')], string='Ticket Type', select=True)
    engineer_ids = fields.Many2many('res.users',string='Engineers')
    ticket_cost_ids = fields.One2many('kin.ticket.cost','ticket_id',string='Costs')




