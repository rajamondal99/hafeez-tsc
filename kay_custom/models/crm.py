from openerp import models, fields,api
from datetime import datetime
from openerp.addons.base.res.res_partner import format_address

from openerp.osv import osv


class CrmExtend(format_address, osv.osv):
    _inherit='crm.lead'

    activity_completed = fields.Many2one("crm.activity", "Completed Activity", select=True)

    @api.onchange('activity_completed')
    @api.multi
    def _compute_state_change(self):
        for rec in self:
            print("soooooo")
            if rec.activity_completed.name =='0%':
                print("here")
                rec.stage_id = self.env['crm.stage'].search([('name','=','0%')]).id
            elif rec.activity_completed.name =='20%':
                rec.stage_id = self.env['crm.stage'].search([('name','=','20%')]).id
            elif rec.activity_completed.name =='50%':
                rec.stage_id = self.env['crm.stage'].search([('name','=','50%')]).id
            elif rec.activity_completed.name =='80%':
                rec.stage_id = self.env['crm.stage'].search([('name','=','80%')]).id
            elif rec.activity_completed.name =='100%':
                rec.stage_id = self.env['crm.stage'].search([('name','=','100%')]).id





