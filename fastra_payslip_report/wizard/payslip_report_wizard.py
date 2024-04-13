# -*- coding: utf-8 -*-

from openerp import models, fields, api
import xlsxwriter
import base64
from io import BytesIO
from datetime import datetime


class FastraPayslipReportWizard(models.TransientModel):
    _name = 'fastra.payslip.report.wizard'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    rule_ids = fields.Many2many('hr.salary.rule', string='Salary Rule')
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_fastra_payslip_rel', 'fastra_payslip_wiz_id', 'fastra_emp_id', string='Employees')
    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('File Name')

    @api.multi
    def fastra_payslip_report(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)

        worksheet = workbook.add_worksheet('Payroll Report')

        start_date = datetime.strptime(self.start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        end_date = datetime.strptime(self.end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        user_company = self.env.user.company_id

        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 24})
        title_format = workbook.add_format({'bold': True, 'underline': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 14})
        cell_wrap_format = workbook.add_format({'valign': 'vjustify', 'font_size': 10})
        cell_total_currency = workbook.add_format({'font_size': 10})
        cell_total_currency.set_num_format('#,#00.00')
        head_format = workbook.add_format({'bold': True})

        # Header Format
        worksheet.set_row(2, 30)  # Set row height
        worksheet.merge_range(2, 2, 2, 9, user_company.name, header_format)

        # Title Format
        worksheet.set_row(4, 20)
        worksheet.merge_range(4, 2, 4, 9, 'Payslip Report from %s to %s ' % (start_date, end_date), title_format)

        col = 2
        row = 5
        worksheet.set_column(4, 4, 50, cell_wrap_format)  # set column width with wrap format.
        worksheet.set_row(row, 20)
        row += 2
        worksheet.write_row(row, col, ('S/N', 'Salary Rule Code', 'Employee', 'Department', 'Total Amount'), head_format)
        row += 1

        for rule in self.rule_ids:
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
            args = (rule.id, tuple(self.employee_ids.ids), self.start_date, self.end_date)
            self.env.cr.execute(sql_statement, args)
            lines = self.env.cr.dictfetchall()

            for line in lines:
                worksheet.write(row, col, line['serial_no'], cell_wrap_format)
                worksheet.write(row, 3, rule.name, cell_wrap_format)
                worksheet.write(row, 4, line['name_related'], cell_total_currency)
                worksheet.write(row, 5, line['name'], cell_wrap_format)
                worksheet.write(row, 6, line['total_amount'], cell_total_currency)
                row += 1

        workbook.close()
        file_data.seek(0)
        self.write(
            {'excel_file': base64.encodestring(file_data.read()),
             'file_name': 'Payroll.xlsx'})

        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=fastra.payslip.report.wizard&id=" + str(self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
            'target': 'current'
        }
