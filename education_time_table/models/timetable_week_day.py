# -*- coding: utf-8 -*-
from odoo import models, fields

class TimetableWeekDay(models.Model):
    _name = 'timetable.week.day'
    _description = 'Timetable Week Day'
    _order = 'sequence'

    name = fields.Char(string='Day Name', required=True, translate=True)
    code = fields.Selection([
        ('0', 'Saturday'),
        ('1', 'Sunday'),
        ('2', 'Monday'),
        ('3', 'Tuesday'),
        ('4', 'Wednesday'),
        ('5', 'Thursday'),
        ('6', 'Friday'),
    ], string='Day Code', required=True, index=True)
    sequence = fields.Integer(string='Sequence', default=10)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code for the week day must be unique !')
    ]
