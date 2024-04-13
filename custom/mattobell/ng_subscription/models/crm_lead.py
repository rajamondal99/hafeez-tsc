# -*- coding: utf-8 -*-

from openerp import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    surname = fields.Char(string='Surname')
    firstname = fields.Char(string='First Name')
    othername = fields.Char(string='Other Name')
    
    sex = fields.Selection(selection=[('male', 'Male'), 
                                      ('female', 'Female')], string='Sex', required=True, default='male')
    marital_status = fields.Selection(selection=[('married', 'Married'), 
                                                 ('single', 'Single'),
                                                 ('others', 'Others')], string='Marital Status', required=True, default='married')
    birth_date = fields.Date(string='Date of Birth')
    nationality_id = fields.Many2one('res.country', string='Nationality', required=True)
#     residential_address = fields.Text(string='Residential Address')
    occupation = fields.Char(string='Occupation')
    employeer = fields.Char(string='Employeer')
    employeer_address = fields.Text(string='Employeer Address')
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

    #Plot Information
    product_template_id = fields.Many2one('product.template', string='Estate')
    estate_id = fields.Many2one('product.product',string='Estate Variant', required=True)
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

    #Marketer Information
    marketer_id = fields.Many2one('sales.agent.partner', string='Name of Marketer')
    marketer_region1 = fields.Many2one('zone.zone', string='Marketers Region')
    marketer_branch1 = fields.Many2one('branch.branch', string='Marketers Branch')
    marketer_phone = fields.Char(string='Marketer’s Phone No')
    subscribe_id = fields.Many2one('customer.subscription', string='Related Subscription')
    payment_plan_dummy = fields.Selection(selection=[(' Full Payment', ' Full Payment'),
                                               ('Monthly', 'Monthly'),
                                               ('3 Months', '3 Months'),
                                               ('6 Months', '6 Months'),
                                               ('12 Months', '12 Months'),
                                               ('24 Months', '24 Months'),
                                               ('36 Months', '36 Months'),
                                               ('48 Months', '48 Months'),
                                               ('60 Months', '60 Months')],  string='Payment Plan', required=True)
    payment_plan = fields.Many2one('product.installment.config', 'Payment Plan', required=False)



    
