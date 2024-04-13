# -*- coding: utf-8 -*-

{
    'name': 'Fastra Payslip Report',
    'version': '0.1',
    'category': 'HR',
    'description': """""",
    'depends': ['base', 'hr', 'hr_payroll', 'hr_expense',
                'hr_attendance', 'hr_holidays', 'hr_contract_operating_unit',
                'kin_report', 'report_xlsx'],
    'data': [
        'wizard/payslip_report_wizard_view.xml',
    ],
    'installable': True,
}
