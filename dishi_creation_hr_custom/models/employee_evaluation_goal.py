# -*- coding: utf-8 -*-
import openerp

from openerp import models, fields, api


class EmployeeEvaluationGoal(models.Model):
    _name = 'employee.evaluation.goal'
    _description = 'Employee Evaluation Goal'

    RATING_CHOICES = [
        ('5', 'Exceptional'),
        ('4', 'Above Expectations'),
        ('3', 'Satisfactory'),
        ('2', 'Improvement Needed'),
        ('1', 'Unsatisfactory'),
    ]

    name = fields.Char(string='Objective/Job Function')
    key_result_areas = fields.Char(string='Key Result Areas')
    outcomes = fields.Char(string='Outcomes')
    employee_rating = fields.Selection(RATING_CHOICES, string='Employee Rating')
    manager_rating = fields.Selection(RATING_CHOICES, string='Manager Rating')
    employee_comments = fields.Text(string='Employee Comments')
    manager_comments = fields.Text(string="Manager's Comments")

    evaluation_id = fields.Many2one(
        'employee.evaluation',
        string='Employee Evaluation',
    )
