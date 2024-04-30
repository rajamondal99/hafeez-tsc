from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError


class Holidays(models.Model):
    _inherit = "hr.holidays"

    def create(self, cr, uid, values, context=None):
        # only hr manager can create leave allocation.
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        group_hr_manager_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_hr_manager')[1]
        group_ids = [g.id for g in user.groups_id]
        if values.get('type') == 'add' and group_hr_manager_id not in group_ids:
            raise ValidationError("You can not create leave allocation because you are not hr manager.")

        return super(Holidays, self).create(cr, uid, values, context)
    @api.one
    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id or self.pending_approver.transfer_holidays_approvals_to_user.id == self.env.user.id:
            self.current_user_is_approver = True
        elif self.department_id.manager_id.user_id.id == self.env.user.id:
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False

    @api.onchange('employee_id')
    def sltech_onchange_employee(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id
        else:
            self.pending_approver = False

    @api.multi
    def action_approve(self):
        for holiday in self:
            user_id = self.env.user.id
            employee = holiday.employee_id
            department = holiday.department_id or employee.department_id

            group_hr_manager_id = self.env.ref('base.group_hr_manager')

            # Check holiday status
            if holiday.state not in ['confirm', 'validate1']:
                raise ValidationError("You can not approve the leave because of the state of the leave.")

            if holiday.type == 'remove':
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
                        raise ValidationError("You can not approve the leave. Because you are not manager of the department")

                elif holiday.state == 'validate1':
                    # In this state only HR manager can approve the leave
                    if group_hr_manager_id in self.env.user.groups_id:
                        super(Holidays, self).action_approve()
                    else:
                        raise ValidationError("You can not approve the leave. Because you are not hr manager")

            elif holiday.type == 'add':
                # add mean leave allocation and leave allocation only HR manager can approve
                if group_hr_manager_id in self.env.user.groups_id:
                    super(Holidays, self).action_approve()
                else:
                    raise ValidationError("You can not approve the leave. Because you are not hr manager")

