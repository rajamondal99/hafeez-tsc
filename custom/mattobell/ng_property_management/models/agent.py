# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class SalesAgent(models.Model):
    _name = 'sales.agent'
    _description = 'Sales Agent'
    
    name = fields.Char(string='Name', required=True)

class SalesAgentPartner(models.Model):
    _name = 'sales.agent.partner'
    _description = 'Sales Agent Partner'
    _rec_name = 'agent_id'

    agent_id = fields.Many2one('sales.agent', required=True, string='Marketer')
    partner_id = fields.Many2one('res.partner', required=True, string='Related Partner')
    user_id = fields.Many2one('res.users', required=True, string='Related User')
    zone_id = fields.Many2one('zone.zone', 'Zone', related='partner_id.zone_id')
    branch_id = fields.Many2one('branch.branch', 'Branch', related='partner_id.branch_id')
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
           ('agent_id_uniq',
            'unique(agent_id)',
            'Sales Agent must be unique.'),
       ]
    
class SalesAgentCommision(models.Model):
    _name = 'sales.agent.commision'
    _description = 'Sales Agent Commision'
    
    commission_id = fields.Many2one('sales.agent.partner', required=False, string='Commission')
    number_of_months = fields.Integer(string='Number of Months', required=True)
    commission_percentage = fields.Float(string='Commission Percentage', required=True)

class Zones(models.Model):
    _name = 'zone.zone'
    _description = 'Zones'
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', readonly=True)
    branch_ids = fields.One2many('branch.branch', 'zone_id', 'Branches')
    
    @api.model
    def create(self, vals):
        vals.update(code = self.env['ir.sequence'].next_by_code('zone.code') or '/')
        return super(Zones, self).create(vals)

class Branch(models.Model):
    _name = 'branch.branch'
    _description = 'Branches'
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', readonly=True)
    zone_id = fields.Many2one('zone.zone', 'Zone', required=True)

    @api.model
    def create(self, vals):
        vals.update(code = self.env['ir.sequence'].next_by_code('branch.code') or '/')
        return super(Branch, self).create(vals)


class BranchMarketer(models.Model):
    _name = 'branch.marketer'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Branch Marketer'
    
    zone_id = fields.Many2one('zone.zone', 'Zone', required=True)
    branch_id = fields.Many2one('branch.branch', 'Branch', required=True, track_visibility="onchange")
    marketer_id = fields.Many2one('sales.agent.partner', 'Marketer', required=True, track_visibility="onchange")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('approved', 'Approved'),
                              ('request', 'Request'),
                              ('re_assigned', 'Re-assigned'),
                              ('cancelled', 'Cancelled')], string="State",
                             default='draft',
                             readonly=True,
                             track_visibility="onchange")
    active = fields.Boolean('Active', default=True)

    @api.multi
    @api.depends('zone_id', 'branch_id', 'marketer_id')
    def name_get(self):
        result = []
        for marketer in self:
            name = marketer.marketer_id.agent_id.name + '-' + marketer.branch_id.name
            result.append((marketer.id, name))
        return result

    @api.multi
    def confirm(self):
        for record in self:
            record.write({'state': 'confirm'})

    @api.multi
    def approve(self):
        for record in self:
            partner = record.marketer_id.partner_id
            partner.write({'zone_id': record.zone_id.id,
                                      'branch_id': record.branch_id.id})
            record.write({'state': 'approved'})

    @api.multi
    def request(self):
        for record in self:
            record.write({'state':'request'})

    @api.multi
    def reassign(self):
        for record in self:
            partner = record.marketer_id.partner_id
            partner.write({'zone_id': record.zone_id.id,
                                      'branch_id': record.branch_id.id})
            record.write({'state': 're_assigned'})

    @api.multi
    def cancel(self):
        for record in self:
            record.write({'state': 'cancelled'})
            
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('name', 'code', 'display_name')
    def name_getdummmy(self):
        result = []
        for partner in self:
            name = partner.customer_uniq_id + ' ' + partner.display_name
            result.append((partner.id, name))
        return result

    @api.multi
    def _customer_accouts_count(self):
        for partner in self:
            partner.contracts_count = self.env['sale.property.reference'].search_count([('partner_id', '=', partner.id)])
            
            
    @api.model
    def create(self, vals):
        if vals.get('customer_uniq_id', '/') == '/' and vals.get('customer', False) and vals['customer']:
            vals['customer_uniq_id'] = self.env['ir.sequence'].next_by_code('res.partner.customer') or '/'
        elif self._context.get('default_customer', False):
            vals['customer_uniq_id'] = self.env['ir.sequence'].next_by_code('res.partner.customer') or '/'
        elif vals.get('customer_uniq_id', '/') == '/' and vals.get('supplier', False) and vals['supplier']:
            vals['customer_uniq_id'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        elif vals.get('agent_uniq_id', '/') == '/' and vals.get('is_agent', False) and vals['is_agent']:
            vals['agent_uniq_id'] = self.env['ir.sequence'].next_by_code('res.partner.agent') or '/'
            
        result = super(ResPartner, self).create(vals)
        return result
    
    is_agent = fields.Boolean(string='Marketer', default=False)
    customer_uniq_id = fields.Char(string='Customer ID', default='/')
    agent_uniq_id = fields.Char(string='Agent ID', default='/')
    zone_id = fields.Many2one('zone.zone', 'Zone', readonly=True, track_visibility="onchange")
    branch_id = fields.Many2one('branch.branch', 'Branch', readonly=True, track_visibility="onchange")
    customer_accouts_count = fields.Integer(compute='_customer_accouts_count', string="Customer Accounts", type='integer')

