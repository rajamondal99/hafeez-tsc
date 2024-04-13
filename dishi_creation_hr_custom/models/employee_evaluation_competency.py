# -*- coding: utf-8 -*-
import openerp

from openerp import models, fields, api


class EmployeeEvaluationCompetency(models.Model):
    _name = 'employee.evaluation.competency'
    _description = 'Employee Evaluation Competency'

    PERFORMANCE_CATEGORIES = [
        ('WORK_QUALITY', 'Work Quality'),
        ('JOB_KNOWLEDGE', 'Job Knowledge'),
        ('DEPENDABILITY_CONSISTENCY', 'Dependability & Consistency'),
        ('COMMUNICATION', 'Communication'),
        ('LISTENING_SKILLS', 'Listening Skills'),
        ('INTERPERSONAL_SKILLS', 'Interpersonal Skills'),
        ('INITIATIVE', 'Initiative'),
        ('TEAMWORK', 'Teamwork'),
        ('ATTENDANCE_PUNCTUALITY', 'Attendance & Punctuality'),
    ]
    RATING_CHOICES = [
        ('5', 'Exceptional'),
        ('4', 'Above Expectations'),
        ('3', 'Satisfactory'),
        ('2', 'Improvement Needed'),
        ('1', 'Unsatisfactory'),
    ]
    performance_category = fields.Selection(PERFORMANCE_CATEGORIES, string='Performance Categories')
    employee_rating = fields.Selection(RATING_CHOICES, string='Employee Rating')
    supervisor_rating = fields.Selection(RATING_CHOICES, string='Supervisor Rating')
    supervisor_comments = fields.Text(string='Supervisor\'s Comments')

    evaluation_id = fields.Many2one(
        'employee.evaluation',
        string='Employee Evaluation',
    )


