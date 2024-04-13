# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class SalesAgent(models.Model):
    _inherit = 'sales.agent'
    
    _rec_name = 'agent_name'
    
    @api.depends('agent_id', 'name')
    def _get_agent_name(self):
        for record in self:
            if not record.agent_id == '/':
                record.agent_name = record.agent_id + '-' + record.name
    
    agent_id = fields.Char('Marketer ID', readonly=True, default='/')
    agent_name = fields.Char(compute='_get_agent_name', string='Marketer Name', store=True)
    
    @api.model
    def create(self, vals):
        if not vals.get('agent_id'):
            vals['agent_id'] = self.env['ir.sequence'].get('sales.agent') or ''
        return super(SalesAgent, self).create(vals)