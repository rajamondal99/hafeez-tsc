
from openerp import models, fields,api
from datetime import datetime


class TimeoutHistory(models.Model):
    _name = 'timeout.history'



    name = fields.Char()
    #user_id = fields.Many2one('res.users',string="Responsible")
    user_id = fields.Char(string="Responsible",readonly=True)
    document_id = fields.Char(String='Reference',readonly=True)
    time_start = fields.Datetime(string="Time Start",readonly=True)
    time_end = fields.Datetime(string="Time End")
    time_range = fields.Char(string="Time Expected")


