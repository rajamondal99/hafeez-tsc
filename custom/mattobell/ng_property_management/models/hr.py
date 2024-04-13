# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    
    zone_id = fields.Many2one('zone.zone', 'Zone', required=False)
    branch_id = fields.Many2one('branch.branch', 'Branch', required=False, track_visibility="onchange")
