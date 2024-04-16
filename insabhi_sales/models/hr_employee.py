import datetime

from openerp import api, fields, models, _


class HrExtend(models.Model):
    _inherit = 'hr.employee'

    exp_rel_pos = fields.Char(string='EXP REl POS')

    @api.model
    def create(self, vals):
        hr = super(HrExtend, self).create(vals)
        leave_id = self.env['hr.holidays'].sudo().create({
            'name': 'Annual Leave ' + str(datetime.datetime.now().year),
            'type': 'add',
            'holiday_type': 'employee',
            'employee_id': hr.id,
            'number_of_days_temp': 18,
            'holiday_status_id': self.env.ref('hr_holidays.holiday_status_cl').id,
            'department_id': hr.department_id.id,
        })
        leave_id.holidays_confirm()
        return hr
