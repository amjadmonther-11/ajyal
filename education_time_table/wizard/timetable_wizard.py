
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TimetableGenerateWizard(models.TransientModel):
    _name = 'timetable.generate.wizard'
    _description = 'Wizard to Generate Timetable'

    class_division = fields.Many2one(
        'education.class.division',
        string='Class',
        required=True,
        readonly=True,
    )

    week_day_ids = fields.Many2many(
        'timetable.week.day',
        string='Select Days',
        required=True,
        help='Select the days for which you want to generate the timetable.'
    )

    generated_schedule_ids = fields.One2many(
        'timetable.generate.schedule',
        'wizard_id',
        string='Generated Timetable',
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_id = self.env.context.get('active_id')
        class_division_id = self.env.context.get('default_class_division')

        if class_division_id:
            class_division = self.env['education.class.division'].browse(class_division_id)
            if class_division.exists():
                res['class_division'] = class_division.id
            else:
                raise UserError(_("The selected class division no longer exists. Please refresh the page."))
        elif active_id:
            class_division = self.env['education.class.division'].browse(active_id)
            if class_division.exists():
                res['class_division'] = class_division.id
            else:
                raise UserError(_("The selected class division no longer exists. Please refresh the page."))
        else:
            raise UserError(_("No class division found in context."))

        return res

    @api.onchange('week_day_ids')
    def _onchange_week_days(self):
        """Populate generated_schedule_ids when days are selected"""
         # 1. Clear any existing lines to start fresh
        self.generated_schedule_ids = [(5, 0, 0)]
        if not self.class_division or not self.week_day_ids:
            return
            

        timetable = self.env['education.timetable'].search([
            ('class_division', '=', self.class_division.id),
        # ('academic_year', '=', self.env.context.get('default_academic_year')),
        ], limit=1)


        # 2. Find the timetable for the current class
        timetable = self.env['education.timetable'].search([
            ('class_division', '=', self.class_division.id),
        ], limit=1)

        if not timetable:
            return

        # 3. Fetch all schedule lines for the selected days
        selected_day_codes = self.week_day_ids.mapped('code')
        schedules = self.env['education.timetable.schedule'].search([
            ('timetable_id', '=', timetable.id),
            ('week_day', 'in', selected_day_codes),
        ])

        # 4. Sort schedules by day and start time to ensure correct order
        # The 'week_day' field in the model is a selection (char), so sorting works directly.

        schedules = sorted(schedules, key=lambda s: (s.week_day, s.period_id.time_from))
        # 5. Build the list of schedule lines directly from the fetched data
        schedule_lines = []
        for schedule in schedules:
            week_day_record = self.env['timetable.week.day'].search([('code', '=', schedule.week_day)], limit=1)

            schedule_lines.append((0, 0, {
                'week_day': week_day_record.id,
                'period_id': schedule.period_id.id,
                'subject_id': schedule.subject.id if schedule.subject else False,
                'faculty_id': schedule.faculty_id.id if schedule.faculty_id else False,
                'start_time': schedule.time_from,
                'end_time': schedule.time_till,
            }))

         # 6. Assign the clean list to the field
        self.generated_schedule_ids = schedule_lines

    def action_generate_timetable(self):
        self.ensure_one()



        if not self.class_division or not self.week_day_ids:
            raise UserError(_("Please select a class and at least one day to generate the timetable."))

        main_timetable_config = self.env['education.timetable'].search([
            ('class_division', '=', self.class_division.id),
        ], limit=1)

        if not main_timetable_config:
            raise UserError(_("A main timetable configuration for this class does not exist. Please create one first."))

        selected_day_codes = self.week_day_ids.mapped('code')
        schedules_to_process = self.env['education.timetable.schedule'].search([
            ('timetable_id', '=', main_timetable_config.id),
            ('week_day', 'in', selected_day_codes),
        ])

        if not schedules_to_process:
            raise UserError(_("No scheduled periods found for the selected days in the main timetable configuration."))

        timetable_record = self.env['education.timetable'].search([
            ('class_division', '=', self.class_division.id),
            ('academic_year', '=', self.class_division.academic_year_id.id)
        ], limit=1)

        if not timetable_record:
            timetable_record = self.env['education.timetable'].create({
                'class_division': self.class_division.id,
                'academic_year': self.class_division.academic_year_id.id,
            })

        schedule_vals_list = []
        for schedule in schedules_to_process:
            schedule_vals_list.append({
                'timetable_id': timetable_record.id,
                'period_id': schedule.period_id.id,
                'subject': schedule.subject.id,
                'faculty_id': schedule.faculty_id.id,
                'week_day': schedule.week_day,
                'time_from': schedule.time_from,
                'time_till': schedule.time_till,
                'class_division': self.class_division.id,
            })

        if schedule_vals_list:
            self.env['education.timetable.schedule'].search([('timetable_id', '=', timetable_record.id)]).unlink()
            self.env['education.timetable.schedule'].create(schedule_vals_list)

        return {
            'name': _('Timetable Schedule'),
            'type': 'ir.actions.act_window',
            'res_model': 'education.timetable.schedule',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {
                'search_default_group_timetable_id': 1,
                'search_default_group_week_day': 1,
            },



        # for line in self.generated_schedule_ids:
        #     self.env['education.timetable.schedule'].create({
        #         'timetable_id': timetable.id,
        #         'class_division': self.class_division.id,
        #         'week_day': line.week_day.id if line.week_day else False,
        #         'period_id': line.period_id.id if line.period_id else False,
        #         'subject': line.subject_id.id if line.subject_id else False,
        #         'faculty_id': line.faculty_id.id if line.faculty_id else False,
        #         'time_from': line.start_time,
        #         'time_till': line.end_time,
        #     })


        #     return {
        #         'name': _('Generated Timetable'),
        #         'type': 'ir.actions.act_window',
        #         'res_model': 'education.timetable.schedule',
        #         'view_mode': 'tree,form',
        #         'domain': [('timetable_id', '=', timetable.id)],
        #         'context': dict(self.env.context),
        #     }



 

    }


        


class TimetableGenerateSchedule(models.TransientModel):
    _name = 'timetable.generate.schedule'
    _description = 'Temporary Timetable Schedule for Wizard'

    wizard_id = fields.Many2one('timetable.generate.wizard', string='Wizard')

    week_day = fields.Many2one('timetable.week.day', string='Week Day', required=True)
    period_id = fields.Many2one('timetable.period', string='Period', required=True)
    subject_id = fields.Many2one('education.subject', string='Subject')
    faculty_id = fields.Many2one('education.faculty', string='Faculty')

    start_time = fields.Float(string='From')
    end_time = fields.Float(string='Till')

    day_header = fields.Char(string='Day', readonly=True)

