# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Aswani PC, Saritha Sahadevan (<https://www.cybrosys.com>)
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
from odoo import models, api, _
from odoo.http import request
from datetime import timedelta, datetime, date


class Attendance(models.Model):
	_inherit = 'education.attendance'

	@api.model
	def get_attendance_details(self):
		current_year = self.env['education.academic.year'].search([('current_year','=',True)])
		student=[]
		atten=0
		absence=0
		invoices =[]
		
		
		schools = self.env['school.school'].sudo().search_read([])
		schools_list = self.env['school.school'].search([])
		

		today = datetime.strftime(datetime.today(), '%Y-%m-%d')
		classes = self.env['education.class.division'].search([('academic_year_id','=',current_year.id)])
		mini = classes.mapped('id')
		
		for school in schools_list:
			sublist=self.env['education.student'].search_count([('school_id','=',school.id),('class_id','in',mini)])
			attendance = self.env['education.attendance'].search([('date','=',today),('division_id.school_id','=',school.id)])
			attend = attendance.mapped('id')
			atten = self.env['education.attendance.line'].search_count([('state','=','attending'),('attendance_id','in',attend)])
			absence = sublist-atten
			student.append([school.id,sublist,atten,absence])
			atten=0
			absence=0

		





		if schools:
			data = {
				'schools':schools,
				'today':today,
				'students': student,
			}
			invoices.append(data)
		return invoices
