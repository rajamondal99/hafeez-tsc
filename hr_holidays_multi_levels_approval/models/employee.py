#-*- coding:utf-8 -*-

from openerp import models, fields, api

class Employee(models.Model):
    _inherit ='hr.employee'

    holidays_approvers = fields.One2many('hr.employee.holidays.approver', 'employee', string='Approvers chain')
    transfer_holidays_approvals_to = fields.Many2one('hr.employee', string='Transfer approval rights to')
    transfer_holidays_approvals_to_user = fields.Many2one('res.users', string='Transfer approval rights to user', related='transfer_holidays_approvals_to.user_id', related_sudo=True, store=True, readonly=True)
    
    
    @api.model
    def get_new_employee_action(self):
        action = self.env.ref('hr.open_view_employee_list_my').read()[0]
        if self.env.user.has_group('base.group_user'):
            action['domain'] = [('user_id','=', self.env.user.id)]
        if self.env.user.has_group('base.group_hr_user') or self.env.user.has_group('base.group_hr_manager'):
            action['domain'] = []
        #print(action)
        return action
    
    @api.multi
    @api.one
    def set_default_validation_chain(self):
        for approver in self.holidays_approvers:
            approver.unlink()
        
        approver = self.parent_id
        sequence = 1
        while True:
            if approver:
                self.env['hr.employee.holidays.approver'].create({'employee': self.id, 'approver': approver.id, 'sequence': sequence})
                approver = approver.parent_id
                sequence = sequence + 1
            else:
                break
