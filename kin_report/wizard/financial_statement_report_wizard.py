# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2017  Kinsolve Solutions
# Copyright 2017 Kingsley Okonkwo (kingsley@kinsolve.com, +2348030412562)
# License: see https://www.gnu.org/licenses/lgpl-3.0.en.html

from openerp import models, fields, api


class FinancialStatementWizard(models.TransientModel):
    _name = 'financial.statement.wizard'

    #     def pdf_report(self, cr, uid, ids, context=None):
    #         context = context or {}
    #         datas = {'name':'PFS Report','ids': context.get('active_ids', [])} # use ids for pdf report otherwise there will be error
    #
    #         return {'type': 'ir.actions.report.xml',
    #                     'report_name': 'pfa.form.pdf.webkit',
    #                     'datas':datas,
    #                     }

    @api.multi
    def financial_statement_report(self):
        context = self.env.context or {}
        wiz_data = self.read([])[0]
        data = {'name': 'Financial Statement Report', 'active_ids': context.get('active_ids', [])}
        data['form'] = {'journal_ids' : wiz_data['journal_ids'],'operating_unit_ids' : wiz_data['operating_unit_ids'],'start_date' : wiz_data['start_date'],'end_date':wiz_data['end_date'],'is_debit_credit': wiz_data['is_debit_credit'],'report_type': wiz_data['report_type']}
        return {
                     'name':'Excel Financial Statement Report',
                     'type': 'ir.actions.report.xml',
                    'report_name': 'kin_report.report_financial_statement',
                    'datas': data,
                    }


    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    is_debit_credit = fields.Boolean('Display Debit/Credit')
    report_type = fields.Selection([('trial_balance',"Trial Balance"),('income_statement', "Income Statement"), ('balance_sheet', "Balance Sheet")],string='Report Type',default='income_statement', required=True)
    operating_unit_ids = fields.Many2many('operating.unit', 'operating_unit_rel', 'financialwizard_id', 'operateunit_id', string='Operating Units',default = lambda self : self.env['operating.unit'].search([]))
    journal_ids = fields.Many2many('account.journal','journal_rel','financialwizard_id','journalid',string='Journals', default = lambda self : self.env['account.journal'].search([]))




