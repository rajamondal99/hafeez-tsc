# -*- coding: utf-8 -*-
import openerp

from openerp import models, fields, api


class EmployeeEvaluationTraining(models.Model):
    _name = 'employee.evaluation.training'
    _description = 'Recommended Trainings for Employee'

    name = fields.Char(string='Training')
    evaluation_id = fields.Many2one(
        'employee.evaluation',
        string='Employee Evaluation',
    )

