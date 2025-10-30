# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Avinash Nk (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class EducationStudentsAttendance(models.Model):
	_name = 'education.attendance'

	name = fields.Char(string='Name', default='New')
	class_id = fields.Many2one('education.class', string='Class')
	division_id = fields.Many2one('education.class.division', string='Division',
		domain="[('academic_year_id', '=', academic_year)]", required=True)
	date = fields.Date(string='Date', default=fields.Date.today, required=True)
	attendance_line = fields.One2many('education.attendance.line', 'attendance_id', string='Attendance Line')
	attendance_created = fields.Boolean(string='Attendance Created')
	all_marked_morning = fields.Boolean(string='All students are present in the morning')
	all_marked_afternoon = fields.Boolean(string='All students are present in the afternoon')
	state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],'Status', default='draft')
	company_id = fields.Many2one('res.company', string='School',
								 default=lambda self: self.env['res.company']._company_default_get())
	academic_year = fields.Many2one('education.academic.year', string='Academic Year',
									default=lambda self: self._get_default(), store=True)
	faculty_id = fields.Many2one('education.faculty', string='Faculty')

	@api.model
	def _get_default(self):
		year = self.env['education.academic.year'].search([])
		year_id=0
		for x in year:
			if(x.current_year==True):
				year_id=x.id
		return year_id


	@api.model_create_multi
	# @api.model
	def create(self, vals):
		res = super(EducationStudentsAttendance, self).create(vals)
		res.class_id = res.division_id.class_id.id
		attendance_obj = self.env['education.attendance']
		already_created_attendance = attendance_obj.search(
			[('division_id', '=', res.division_id.id), ('date', '=', res.date), ('company_id', '=', res.company_id.id)])
		if len(already_created_attendance) > 1:
			raise ValidationError(
				_('Attendance register of %s is already created on "%s"', ) % (res.division_id.name, res.date))
		return res

	# @api.multi
	def create_attendance_line(self):
		self.name = str(self.date)
		attendance_line_obj = self.env['education.attendance.line']
		students = self.division_id.student_ids
		if len(students) < 1:
			raise UserError(_('There are no students in this Division'))
		for student in students:
			data = {
				'name': self.name,
				'attendance_id': self.id,
				'student_id': student.id,
				'student_name': student.name,
				'class_id': self.division_id.class_id.id,
				'division_id': self.division_id.id,
				'date': self.date,
			}
			attendance_line_obj.create(data)
		self.attendance_created = True

	# @api.multi
	def mark_all_present_morning(self):
		for records in self.attendance_line:
			records.present_morning = True
		self.all_marked_morning = True

	# @api.multi
	def un_mark_all_present_morning(self):
		for records in self.attendance_line:
			records.present_morning = False
		self.all_marked_morning = False

	# @api.multi
	def mark_all_present_afternoon(self):
		for records in self.attendance_line:
			records.present_afternoon = True
		self.all_marked_afternoon = True

	# @api.multi
	def un_mark_all_present_afternoon(self):
		for records in self.attendance_line:
			records.present_afternoon = False
		self.all_marked_afternoon = False

	# @api.multi
	def attendance_done(self):
		for records in self.attendance_line:
			# records.state = 'done'
			if not records.present_morning and not records.present_afternoon:
				records.full_day_absent = 1
			elif not records.present_morning:
				records.half_day_absent = 1
			elif not records.present_afternoon:
				records.half_day_absent = 1
			records.state = 'done'
		self.state = 'done'

	# @api.multi
	def set_to_draft(self):
		
		self.state = 'draft'


class EducationAttendanceLine(models.Model):
	_name = 'education.attendance.line'

	name = fields.Char(string='Name')
	attendance_id = fields.Many2one('education.attendance', string='Attendance Id')
	student_id = fields.Many2one('education.student', string='Student')
	student_name = fields.Char(string='Student name', related='student_id.name', store=True)
	class_id = fields.Many2one('education.class', string='Class', required=True)
	division_id = fields.Many2one('education.class.division', string='Division', required=True)
	date = fields.Date(string='Date', required=True)
	present_morning = fields.Boolean(string='Morning')
	present_afternoon = fields.Boolean(string='After Noon')
	full_day_absent = fields.Integer(string='Full Day')
	half_day_absent = fields.Integer(string='Half Day')
	state = fields.Selection([('draft', 'Draft'), ('done', 'Done'),('absence', 'Absence'), ('attending', 'Attending')], string='Status', default='attending')
	absence_type = fields.Selection([('reason', 'With reason'), ('no_reason', 'No reason')], string='Absence type')
	absence_reason = fields.Char(string='Absence Reason')

	company_id = fields.Many2one('res.company', string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())
	academic_year = fields.Many2one('education.academic.year', string='Academic Year',
									related='division_id.academic_year_id', store=True)
	main_state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],'Status',related='attendance_id.state' ,default='draft')


	# @api.multi
	def action_attending(self):
		'''Changes the state to done'''
		self.write({'state': 'attending'})

	# @api.multi
	def action_absence(self):
		'''Changes the state to done'''
		self.write({'state': 'absence'})

