
from odoo import models, fields, _

class TimetableWeekDay(models.Model):
    _name = 'timetable.week.day'
    _description = _('Timetable Week Day')
    _order = 'sequence'

    name = fields.Char(string=_('Day Name'), required=True, translate=True)

    code = fields.Selection([
        ('0', _('Saturday')),
        ('1', _('Sunday')),
        ('2', _('Monday')),
        ('3', _('Tuesday')),
        ('4', _('Wednesday')),
        ('5', _('Thursday')),
        ('6', _('Friday')),
    ], string=_('Day Code'), required=True, index=True)

    sequence = fields.Integer(string=_('Sequence'), default=10)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', _('The code for the week day must be unique!'))
    ]
