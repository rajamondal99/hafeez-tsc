import datetime

from openerp import api, fields, models, _


class HrExtend(models.Model):
    _inherit = 'hr.employee'

    exp_rel_pos = fields.Char(string='EXP REl POS')

    @api.model
    def create(self, vals):
        hr = super(HrExtend, self).create(vals)
        self.create_leave_allocation(hr)
        return hr

    @api.model
    def create_leave_allocation_for_old_employee(self):
        employees = self.search([])
        for emp in employees:
            leave_id = self.env['hr.holidays'].search([('employee_id', '=', emp.id), ('holiday_status_id', '=', self.env.ref('hr_holidays.holiday_status_cl').id),('number_of_days_temp', '=', 18.0)])
            if not leave_id:
                self.create_leave_allocation(emp)

    def create_leave_allocation(self, employee, number_of_leaves=18.0):
        leave_id = self.env['hr.holidays'].sudo().create({
            'name': 'Annual Leave ' + str(datetime.datetime.now().year),
            'type': 'add',
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'number_of_days_temp': number_of_leaves,
            'holiday_status_id': self.env.ref('hr_holidays.holiday_status_cl').id,
            'department_id': employee.department_id.id,
        })
        leave_id.holidays_confirm()

    @api.model
    def carry_forward_leaves(self):
        emp_ids = self.search([])
        for emp in emp_ids:
            total_leaves_for_next_year = emp.remaining_leaves + 18.0
            self.create_leave_allocation(emp, total_leaves_for_next_year)