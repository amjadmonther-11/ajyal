

from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError, Warning as UserError
from odoo.exceptions import ValidationError,   UserError

class EducationTimeTable(models.Model):
    _name = 'education.timetable'
    _description = 'Timetable'


    active = fields.Boolean('Active', default=True)
    name = fields.Char(compute='get_name')
    # class_division = fields.Many2one('education.division', string='Class', domain="[('academic_year_id', '=', academic_year)]",required=True)
    class_division = fields.Many2one('education.class.division', string='Class', domain="[('academic_year_id', '=', academic_year)]",required=True)
    class_name = fields.Many2one('education.class', string="Standard")
    division_name = fields.Many2one('education.division', string='Division')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year', default=lambda self: self._get_default(),readonly=True,store=True)
    timetable_sat = fields.One2many('education.timetable.schedule', 'timetable_id',
                                    domain=[('week_day', '=', '0')])
    timetable_sun= fields.One2many('education.timetable.schedule', 'timetable_id',
                                    domain=[('week_day', '=', '1')])
    timetable_mon = fields.One2many('education.timetable.schedule', 'timetable_id',
                                    domain=[('week_day', '=', '2')])
    timetable_tue = fields.One2many('education.timetable.schedule', 'timetable_id',
                                     domain=[('week_day', '=', '3')])
    timetable_wed = fields.One2many('education.timetable.schedule', 'timetable_id',
                                    domain=[('week_day', '=', '4')])
    timetable_thur = fields.One2many('education.timetable.schedule', 'timetable_id',
                                    domain=[('week_day', '=', '5')])
    timetable_fri = fields.One2many('education.timetable.schedule', 'timetable_id',
                                    domain=[('week_day', '=', '6')])
    company_id = fields.Many2one('res.company', string='School',
                                 default=lambda self: self.env['res.company']._company_default_get())
    @api.model
    def _get_default(self):
        """ To get current academic year from academic year model """
        year = self.env['education.academic.year'].search([])
        year_id=0
        for x in year:
            if(x.active==True):
                year_id=x.id
        return year_id

    def get_name(self):
        """To generate name for the model"""
        for i in self:
            i.name = str(i.class_division.name) + "/" + str(i.academic_year.name)

    @api.onchange('class_division')
    @api.constrains('class_division')
    def onchange_class_division(self):
        """To get class and division details from Class Division model"""
        for i in self:
            i.class_name = i.class_division.class_id
            i.division_name = i.class_division.division_id
            # i.academic_year = i.class_division.academic_year_id
            # i.write({'academic_year': i.class_division.academic_year_id})

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
    _description = 'Timetable Schedule'
    _rec_name = 'period_id'

    period_id = fields.Many2one('timetable.period', string="Period", required=True)
    check_period = fields.Boolean(string='Period Type',compute='_check_period_type', store=True)
    time_from = fields.Float(string='From', required=True,
                             index=True, help="Start and End time of Period.")
    time_till = fields.Float(string='Till', required=True)
    subject = fields.Many2one('education.subject', string='Subjects')
    faculty_id = fields.Many2one('education.faculty', string='Faculty')
    week_day = fields.Selection([
        ('0', 'Saturday'),
        ('1', 'Sunday'),
        ('2', 'Monday'),
        ('3', 'Tuesday'),
        ('4', 'Wednesday'),
        ('5', 'Thursday'),
        ('6', 'Friday'),
    ], 'Week day', required=True,default='1')
    timetable_id = fields.Many2one('education.timetable',store=True)
    class_division = fields.Many2one('education.class.division', string='Class', readonly=True)
    company_id = fields.Many2one('res.company', string='School',
                                 default=lambda self: self.env['res.company']._company_default_get())
    # _sql_constraints = [('faculty_uniq', 'unique(faculty_id,week_day,period_id)',
    # #                      'This teacher has a lecture in the same time!')]
    # def write(self, vals):
    #   res = super().write(vals)
    #   if 'week_day' in vals:
    #       for period in self:
    #           schedules = self.env['education.timetable.schedule'].search([('period_id', '=', period.id)])
    #           for sched in schedules:
    #               sched.week_day = vals['week_day']
    #   return res  
    @api.constrains('faculty_id')
    # @api.constrains('faculty_id', 'week_day', 'period_id')
    def _check_faculty_id(self):
        for record in self:
            # record_ids = self.env['education.timetable.schedule'].search([('id','=', self.env.context.get('active_id'))])
            record_ids = self.env['education.timetable.schedule'].search([('id','>=',0)])
            for rec in record_ids:
                if rec.id != self.id:
                # raise ValidationError(rec)
                    if rec.faculty_id == self.faculty_id and rec.week_day == self.week_day and rec.period_id == self.period_id:
                        raise ValidationError("This teacher has a lecture in the same time!")
                    

    @api.model
    def create(self, vals):
        if 'week_day' not in vals and 'default_week_day' in self._context:
            vals['week_day'] = self._context['default_week_day']
        res = super(EducationTimeTableSchedule, self).create(vals)
        res.class_division = res.timetable_id.class_division.id
        return res

        

    @api.onchange('period_id')
    def onchange_period_id(self):
        """Gets the start and end time of the period"""
        for i in self:
            i.time_from = i.period_id.time_from
            i.time_till = i.period_id.time_to
            i.week_day = i.period_id.week_day


    @api.depends('period_id')
    def _check_period_type(self):
        for rec in self:
            for period in rec.period_id:
                if period.activity == True:
                    self.check_period = True
                else:
                    self.check_period = False


class TimetablePeriod(models.Model):
    _name = 'timetable.period'
    _description = 'Timetable Period'

    name = fields.Char(string="Name", required=True,)
    time_from = fields.Float(string='From', required=True,
                             index=True, help="Start and End time of Period.")
    time_to = fields.Float(string='To', required=True)
    company_id = fields.Many2one('res.company', string='School',
                                 default=lambda self: self.env['res.company']._company_default_get())
    activity = fields.Boolean(string='Activity')


    week_day = fields.Selection([
        ('0', 'Saturday'),
        ('1', 'Sunday'),
        ('2', 'Monday'),
        ('3', 'Tuesday'),
        ('4', 'Wednesday'),
        ('5', 'Thursday'),
        ('6', 'Friday'),
    ], string='Week Day' ,default='1')