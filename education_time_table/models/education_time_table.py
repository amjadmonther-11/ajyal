from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class EducationTimeTable(models.Model):
    _name = 'education.timetable'
    _description = _('Timetable')

    active = fields.Boolean(_('Active'), default=True)
    name = fields.Char(compute='get_name')

    class_division = fields.Many2one(
        'education.class.division',
        string=_('Class'),
        domain="[('academic_year_id', '=', academic_year)]",
        required=True
    )

    class_name = fields.Many2one('education.class', string=_("Standard"))
    division_name = fields.Many2one('education.division', string=_('Division'))

    academic_year = fields.Many2one(
        'education.academic.year',
        string=_('Academic Year'),
        default=lambda self: self._get_default(),
        readonly=True,
        store=True
    )

    timetable_sat = fields.One2many(
        'education.timetable.schedule', 'timetable_id',
        domain=[('week_day', '=', '0')], string=_('Saturday')
    )
    timetable_sun = fields.One2many(
        'education.timetable.schedule', 'timetable_id',
        domain=[('week_day', '=', '1')], string=_('Sunday')
    )
    timetable_mon = fields.One2many(
        'education.timetable.schedule', 'timetable_id',
        domain=[('week_day', '=', '2')], string=_('Monday')
    )
    timetable_tue = fields.One2many(
        'education.timetable.schedule', 'timetable_id',
        domain=[('week_day', '=', '3')], string=_('Tuesday')
    )
    timetable_wed = fields.One2many(
        'education.timetable.schedule', 'timetable_id',
        domain=[('week_day', '=', '4')], string=_('Wednesday')
    )
    timetable_thur = fields.One2many(
        'education.timetable.schedule', 'timetable_id',
        domain=[('week_day', '=', '5')], string=_('Thursday')
    )
    timetable_fri = fields.One2many(
        'education.timetable.schedule', 'timetable_id',
        domain=[('week_day', '=', '6')], string=_('Friday')
    )

    company_id = fields.Many2one(
        'res.company', string=_('School'),
        default=lambda self: self.env['res.company']._company_default_get()
    )

    @api.model
    def _get_default(self):
        year = self.env['education.academic.year'].search([])
        for x in year:
            if x.active:
                return x.id
        return False

    def get_name(self):
        for i in self:
            i.name = f"{i.class_division.name}/{i.academic_year.name}"

    @api.onchange('class_division')
    @api.constrains('class_division')
    def onchange_class_division(self):
        for i in self:
            i.class_name = i.class_division.class_id
            i.division_name = i.class_division.division_id

    def action_open_generate_wizard(self):
        self.ensure_one()

        if not self.class_division or not self.class_division.exists():
            raise UserError(_("This record’s class division no longer exists. Please reassign a valid class."))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate Timetable'),
            'res_model': 'timetable.generate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_class_division': self.class_division.id,
            }
        }


class EducationTimeTableSchedule(models.Model):
    _name = 'education.timetable.schedule'
    _description = _('Timetable Schedule')
    _rec_name = 'period_id'

    period_id = fields.Many2one('timetable.period', string=_("Period"), required=True)
    check_period = fields.Boolean(string=_('Period Type'), compute='_check_period_type', store=True)

    time_from = fields.Float(string=_('From'), required=True)
    time_till = fields.Float(string=_('Till'), required=True)

    subject = fields.Many2one('education.subject', string=_('Subject'))
    faculty_id = fields.Many2one('education.faculty', string=_('Faculty'))

    week_day = fields.Selection([
        ('0', _('Saturday')),
        ('1', _('Sunday')),
        ('2', _('Monday')),
        ('3', _('Tuesday')),
        ('4', _('Wednesday')),
        ('5', _('Thursday')),
        ('6', _('Friday')),
    ], string=_('Week Day'), required=True, default='1')

    timetable_id = fields.Many2one('education.timetable', store=True, string=_('Timetable'))
    class_division = fields.Many2one('education.class.division', string=_('Class'), readonly=True)

    company_id = fields.Many2one(
        'res.company', string=_('School'),
        default=lambda self: self.env['res.company']._company_default_get()
    )

    @api.constrains('faculty_id')
    def _check_faculty_id(self):
        for record in self:
            if not record.faculty_id:
                continue

            conflict = self.env['education.timetable.schedule'].search([
                ('id', '!=', record.id),
                ('faculty_id', '=', record.faculty_id.id),
                ('week_day', '=', record.week_day),
            ])

            for rec in conflict:
                overlapping = (
                    record.time_from < rec.time_till and
                    record.time_till > rec.time_from
                )
                if overlapping:
                    raise ValidationError(_("This teacher already has another class at the same time!"))

    @api.model
    def create(self, vals):
        if 'week_day' not in vals and 'default_week_day' in self._context:
            vals['week_day'] = self._context['default_week_day']
        res = super().create(vals)
        res.class_division = res.timetable_id.class_division.id
        return res

    @api.onchange('period_id')
    def onchange_period_id(self):
        for i in self:
            i.time_from = i.period_id.time_from
            i.time_till = i.period_id.time_to
            i.week_day = i.period_id.week_day

    @api.depends('period_id')
    def _check_period_type(self):
        for rec in self:
            rec.check_period = True if rec.period_id.activity else False


class TimetablePeriod(models.Model):
    _name = 'timetable.period'
    _description = _('Timetable Period')

    name = fields.Char(string=_("Name"), required=True)
    time_from = fields.Float(string=_('From'), required=True)
    time_to = fields.Float(string=_('To'), required=True)

    company_id = fields.Many2one(
        'res.company', string=_('School'),
        default=lambda self: self.env['res.company']._company_default_get()
    )

    activity = fields.Boolean(string=_('Activity'))

    week_day = fields.Selection([
        ('0', _('Saturday')),
        ('1', _('Sunday')),
        ('2', _('Monday')),
        ('3', _('Tuesday')),
        ('4', _('Wednesday')),
        ('5', _('Thursday')),
        ('6', _('Friday')),
    ], string=_('Week Day'), default='1')
