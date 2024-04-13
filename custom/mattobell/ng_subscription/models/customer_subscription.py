# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, RedirectWarning, ValidationError


class CustomerSubscription(models.Model):
    _name = 'customer.subscription'
    _description = 'Subscriber Form'
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'code'
    
    @api.one
    def copy(self, default=None):
        raise ValidationError('Sorry! You can not duplicate subscriber.')
        return super(CustomerSubscription, self).copy(default)

    @api.model
    def _get_country(self):
        return self.env['res.country'].search([('code','=','NG')]).id
        
    state = fields.Selection(selection=[
                        ('draft', 'Draft'),
                        ('validated', 'Validated'),
                        ('approved', 'Approved'),
                        ('cancelled', 'Cancelled'),],string='State',
                        readonly=True, default='draft', \
                        track_visibility='onchange')
    title = fields.Selection(selection=[('mr', 'Mr'), 
                                        ('mrs', 'Mrs'), 
                                        ('miss', 'Miss'), 
                                        ('prof', 'Prof'), 
                                        ('dr', 'Dr'),
                                        ('chief', 'Chief')], string='Title', required=True, default='mr')
    surname = fields.Char(string='Surname', required=True)
    firstname = fields.Char(string='First Name', required=True)
    othername = fields.Char(string='Other Name')
    contact_name = fields.Char(compute='combine_contact_name', string="Contact Name")
    
    sex = fields.Selection(selection=[('male', 'Male'),
                                      ('female', 'Female')], string='Sex', required=True, default='male')
    marital_status = fields.Selection(selection=[('married', 'Married'), 
                                                 ('single', 'Single'),
                                                 ('others', 'Others')], string='Marital Status', required=True, default='married')
    birth_date = fields.Date(string='Date of Birth')
    nationality_id = fields.Many2one('res.country', string='Nationality', default=_get_country)
#     residential_address = fields.Text(string='Residential Address')

    street =  fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True, size=24)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", 'State')
    country_id = fields.Many2one('res.country', 'Country')
    
    tel_no = fields.Char(string='Tel No')
    email = fields.Char(string='Email')
    occupation = fields.Char(string='Occupation')
    employeer = fields.Char(string='Employer')
    employeer_address = fields.Text(string='Employer Address')
    next_kin = fields.Char(string='Next of Kin')
    next_kin_relationship = fields.Selection(selection=[('select', 'Select'), 
                                                   ('spouse', 'Spouse'),
                                                   ('brother', 'Brother'),
                                                   ('sister', 'Sister'),
                                                   ('father', 'Father'),
                                                   ('mother', 'Mother'),
                                                   ('others', 'Others'),
                                                   ], string='Next of Kin Relationship', required=True, default='others')
    next_kin_address = fields.Text(string='Address of Next of Kin')
    next_kin_tel_no = fields.Char(string='Tel No of Next of Kin')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string='Company', readonly=True)

    #Plot Information
    product_template_id = fields.Many2one('product.template', string='Estate')
    estate_id = fields.Many2one('product.product',string='Plot Size', required=True)
    lead_id = fields.Many2one('crm.lead',string='Opportunity')
    plot_no = fields.Selection(selection=[('1', '1'), 
                                          ('2', '2'),
                                          ('3', '3'),
                                          ('4', '4'),
                                          ('5', '5'),
                                          ('6', '6'),
                                          ('7', '7'),
                                          ('8', '8'),
                                          ('9', '9'),
                                          ('10', '10'),
                                          ], string='No of Plot', required=True, default='1')
    plot_size = fields.Char(string='Plot Size')
    
    #Building Information
    bulding_type = fields.Selection(selection=[('residential', 'Residential'), 
                                               ('commercial', 'Commercial')],  string='Type of Building', required=True)
    purpose = fields.Selection(selection=[('investment', 'Investment'),
                                          ('residential', 'Residential'), 
                                          ('commercial', 'Commercial')],  string='Purpose', required=True)
    code = fields.Char('Subscription Ref:')
    #Marketer Information
    marketer_id = fields.Many2one('sales.agent.partner', string='Name of Marketer', required=True)
    marketer_region1 = fields.Many2one('zone.zone', string='Marketers Region',required=True)
    marketer_branch1 = fields.Many2one('branch.branch', string='Marketers Branch',required=True)
    marketer_phone = fields.Char(string='Marketer’s Phone No')
    payment_plan_dummy = fields.Selection(selection=[(' Full Payment', ' Full Payment'),
                                               ('Monthly', 'Monthly'),
                                               ('3 Months', '3 Months'),
                                               ('6 Months', '6 Months'),
                                               ('12 Months', '12 Months'),
                                               ('24 Months', '24 Months'),
                                               ('36 Months', '36 Months'),
                                               ('48 Months', '48 Months'),
                                               ('60 Months', '60 Months')],  string='Payment Plan', required=True)
    payment_plan = fields.Many2one('product.installment.config', 'Payment Plan', required=True)

    customer_uniq_id = fields.Char(related='partner_id.customer_uniq_id', string='Customer ID', default='/', readonly=True, store=True)

    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    invoice_id = fields.Many2one('account.invoice', 'Invoice', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer')
    generate_property_ref = fields.Boolean('Generate New Property Ref', default=True)
    create_installment_inv = fields.Boolean('Create Installment Invoices?', default=False, help='Tick this box if you want to create installment invoices along with full invoice.')
    invoice_ids =  fields.One2many('account.invoice', 'sub_scription_id', 'Related Invoices')
    installment_created = fields.Boolean('Installment Invoices Created')

    @api.multi
    def action_view_invoice(self):
        invoice_ids = [i.id for i in self.invoice_ids] 
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % invoice_ids
        elif len(invoice_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = invoice_ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    @api.one
    def get_validate(self):
        self.state = 'validated'
        lead_obj = self.env['crm.lead']
        code = self.env['ir.sequence'].next_by_code('sub.subscription') or '/'
        self.code = code
        vals = {
                'name' : self.contact_name,
                'contact_name' : self.contact_name,
#                 'title' : self.title,
                'surname' : self.surname,
                'firstname' : self.firstname,
                'othername' : self.othername,
                'sex' : self.sex,
                'type': 'opportunity',
                'marital_status' : self.marital_status,
                'birth_date' : self.birth_date,
                'nationality_id' : self.nationality_id.id,
#                 'residential_address' : self.residential_address,
                'street' : self.street,
                'street2' : self.street2,
                'city' : self.city,
                'state_id' : self.state_id.id,
                'zip' : self.zip,
                'country_id' : self.country_id.id,
                'subscribe_id': self.id,
                'phone' : self.tel_no,
                'email_from' : self.email,
                'occupation' : self.occupation,
                'employeer' : self.employeer,
                'employeer_address' : self.employeer_address,
                'next_kin' : self.next_kin,
                'next_kin_relationship' : self.next_kin_relationship,
                'next_kin_address': self.next_kin_address,
                'next_kin_tel_no' : self.next_kin_tel_no,
                'company_id' : self.company_id.id,
                
                'product_template_id' : self.product_template_id.id,
                'estate_id' : self.estate_id.id,
                'plot_no' : self.plot_no,
                'plot_size' : self.estate_id.name,
                'bulding_type' : self.bulding_type,
                'purpose' : self.purpose,
                'marketer_id': self.marketer_id.id,
                'marketer_region1': self.marketer_region1.id,
                'marketer_branch1' : self.marketer_branch1.id,
                'marketer_phone': self.marketer_phone,
                'payment_plan' : self.payment_plan.id,
                }
        lead_id = lead_obj.create(vals)
        self.lead_id = lead_id.id
        return lead_id
    
    
    @api.multi
    def get_approve(self):
        if not self.partner_id:
            raise ValidationError('Please select Customer.')
        self.state = 'approved'
        return True
        
    @api.one
    def get_cancel(self):
        self.state = 'cancelled'
        
        
    @api.multi
    def action_subscription_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template = self.env.ref('ng_subscription.email_template_edi_subscription')
        except ValueError:
            template = False
            
        msg_id = template.send_mail(self.id)
        return msg_id

    @api.multi
    def _prepare_invoice(self, lines):
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        payment_term = self.env['account.payment.term'].search([('name', 'ilike', 'Immediate Payment')])
        invoice_vals = {
            'name': self.code or '',
            'origin': self.code,
            'type': 'out_invoice',
            'account_id': self.partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal_id,
            'currency_id': self.company_id.currency_id.id,
            'payment_term_id': payment_term and payment_term.id or False,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'agent_id': self.marketer_id and self.marketer_id.agent_id.id or False,
            'branch_id': self.marketer_branch1 and self.marketer_branch1.id or False,
            'need_property_ref': False, #since it has been created on main invoice..full invoice.
            'apply_sales_commission': True,
            'is_deferred_account': False,
            'agent_commision': self.payment_plan.agent_commision,
            'invoice_line_ids': lines,
            'sub_scription_id':self.id
        }
        return invoice_vals

    @api.multi
    def action_invoice_create_installment(self):
        for sub in self:
            for x in range(0, self.payment_plan.total_number_installment):
                line_account = self.estate_id.property_account_income_id.id
                if self.generate_property_ref:
                    if not self.estate_id.property_deferred_account_id:
                        raise UserError('Please define deferred income account on estate.')
                    line_account = self.estate_id.property_deferred_account_id.id

                lines = [(0,0,{'name' :  self.estate_id.name + '\n' + 'Payment Plan:-' + self.payment_plan.name, 
                        'origin':  self.code,
                        'uos_id':  False,
                        'product_id':  self.estate_id.id,
                        'property_installment_id':  self.payment_plan.id,
                        'account_id':  line_account, 
                        'price_unit':  self.payment_plan.total_sale_price / self.payment_plan.total_number_installment,#to do fix for outright ?
                        #'preoperty_ref_id': property,
                        'quantity' : self.plot_no , 
                        'agent_commision': self.payment_plan.agent_commision,
                        'partner_id':  self.partner_id.id })]
                inv_data = sub._prepare_invoice(lines)
                if sub.payment_plan:
                    inv_data.update({'use_installment_invoice': True})
                #inv_data.update({'sale_installment_id': sub.id,
                #                 'use_installment_invoice': self.use_installment_invoice})
                invoice = self.env['account.invoice'].create(inv_data)
            sub.installment_created = True
            
    @api.multi
    def action_invoice_create(self):
        self.ensure_one()
        line_account = self.estate_id.property_account_income_id.id
        if self.generate_property_ref:
            if not self.estate_id.property_deferred_account_id:
                raise UserError('Please define deferred income account on estate.')
            line_account = self.estate_id.property_deferred_account_id.id

        property = False
        if self.generate_property_ref:
            number = self.env['ir.sequence'].next_by_code('property.number')
            property = self.env['sale.property.reference'].\
                create({'name': number, 
                        'partner_id': self.partner_id.id,
                       })
        property = property and property.id or False
        
        lines = [(0,0,{'name' :  self.estate_id.name + '\n' + 'Payment Plan:-' + self.payment_plan.name, 
                'origin':  self.code,
                'uos_id':  False,
                'product_id':  self.estate_id.id,
                'property_installment_id':  self.payment_plan.id,
                'account_id':  line_account, 
                'price_unit':  self.payment_plan.total_sale_price,#to do fix for outright ?
                'preoperty_ref_id': property,
                'quantity' : self.plot_no , 
                'agent_commision': self.payment_plan.agent_commision,
                'partner_id':  self.partner_id.id })]
        
        payment_term = self.env['account.payment.term'].search([('name', 'ilike', 'Immediate Payment')])
        vals = {
            'date_invoice': fields.Date.today(),
            'partner_id': self.partner_id.id,
            'account_id': self.partner_id.property_account_receivable_id.id,
            'invoice_line_ids': lines,
            'type': 'out_invoice',
            'name': self.code or False,
            'currency_id': self.company_id.currency_id.id,
            'agent_id': self.marketer_id and self.marketer_id.agent_id.id or False,
            'branch_id': self.marketer_branch1 and self.marketer_branch1.id or False,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'payment_term_id': payment_term and payment_term.id or False,
            'need_property_ref': self.generate_property_ref,
            'apply_sales_commission': True,
            'is_deferred_account': self.generate_property_ref,
            'agent_commision': self.payment_plan.agent_commision,
            'sub_scription_id':self.id
        }
#         if self.payment_plan:
#             vals.update(use_installment_invoice=True)

            #create invoice for cheque return charges by bank
        invoice_id = self.env['account.invoice'].create(vals)
        self.invoice_id = invoice_id
        return True


    @api.multi
    @api.depends('surname','firstname','othername')
    def combine_contact_name(self):
        for line in self:
            surname = line.surname and line.surname or ''
            firstname = line.firstname and line.firstname or ''
            othername = line.othername and line.othername or ''
            line.contact_name = firstname +'    '+ othername +'    '+ surname
            
    @api.onchange('marketer_id')
    def get_marketer_detail(self):
        for line in self:
            line.marketer_region1 = line.marketer_id.zone_id.id
            line.marketer_branch1 = line.marketer_id.branch_id.id
            line.marketer_phone = line.marketer_id.user_id.phone

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    sub_scription_id = fields.Many2one('customer.subscription', string='Subscription Reference', copy=False, readonly=True)

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
