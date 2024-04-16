from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError


class Holidays(models.Model):
    _inherit = "hr.holidays"

    @api.multi
    def action_approve(self):
        for holiday in self:
            user_id = self.env.user.id
            employee = holiday.employee_id
            department = holiday.department_id or employee.department_id
            # Check holiday status
            if holiday.state not in ['confirm', 'validate1']:
                raise ValidationError("You can not approve the leave because of the state of the leave.")

            if holiday.state == 'confirm':
                # In this state only manager can approve the leave
                dept_manager = department.manager_id
                # if department manager is set and current user is the same. So approve it.
                if dept_manager and dept_manager.user_id.id == user_id:
                    self.holidays_first_validate()
                elif not dept_manager:
                    # If Manager is not set, In this case other employees of the same department can approve the leave.

                    # Trying to find the employee of the current user. So we can compare department.
                    current_user_employee = self.env['hr.employee'].search([('user_id', '=', user_id)])

                    if current_user_employee and current_user_employee.department_id == department.id:
                        self.holidays_first_validate()
                    else:
                        raise ValidationError("You can not approve the leave. Because you are not belongs to the department.")
                else:
                    raise ValidationError("You can not approve the leave. Because you are not manager")

            elif holiday.state == 'validate1':
                # In this state only HR manager can approve the leave
                hr_manager = department.hr_manager_id
                if hr_manager and hr_manager.user_id.id == user_id:
                    super(Holidays, self).action_approve()
                else:
                    raise ValidationError("You can not approve the leave. Because you are not hr manager")


