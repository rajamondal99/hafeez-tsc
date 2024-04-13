# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html

from openerp import models, fields, api

class PayslipReportParser(models.TransientModel):

    _name = 'payslip.report.parser'

    def _get_payslip_report_data(self,form):
        start_date = form['start_date']
        end_date = form['end_date']
        employee_ids = form['employee_ids']
        rule_id = form['rule_id']

        #payslip_line_obj = self.env['hr.payslip.line']
        # payslip_lines = payslip_line_obj.search(
        #     [('date_from', '>=', start_date), ('date_to', '<=', end_date), ('employee_id', 'in', employee_ids),
        #      ('salary_rule_id', '=', rule_id[0])],order="employee_id desc")

        sql_statement = """
                    SELECT
                        row_number() over(order by hr_department.name asc) as serial_no,
                        hr_employee.name_related,
                        hr_salary_rule.name,
                        hr_department.name,
                        sum(hr_payslip_line.total) as total_amount
                    FROM
                        hr_payslip_line
                        INNER JOIN hr_salary_rule ON  hr_payslip_line.salary_rule_id = hr_salary_rule.id
                        INNER JOIN hr_employee ON hr_payslip_line.employee_id = hr_employee.id
                        INNER JOIN hr_department ON hr_employee.department_id = hr_department.id
                    WHERE
                          hr_payslip_line.salary_rule_id = %s AND
                          hr_payslip_line.employee_id in %s AND
                          hr_payslip_line.date_from >= %s AND
                          hr_payslip_line.date_to <= %s
                    GROUP BY
                          hr_salary_rule.name,
                          hr_department.name ,
                          hr_employee.name_related;
                    """
        args = (rule_id[0], tuple(employee_ids), start_date, end_date,)
        self.env.cr.execute(sql_statement, args)
        dictAll = self.env.cr.dictfetchall()

        return dictAll





