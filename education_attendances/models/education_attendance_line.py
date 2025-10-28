# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Raneesha M K (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields,api


class EducationAttendanceLine(models.Model):
    """Used for managing attendance shift details"""
    _name = 'education.attendance.line'
    _description = 'Attendance Lines'

    name = fields.Char(string='Name', help="Name of Attendance")
    attendance_id = fields.Many2one('education.attendance',
                                    string='Attendance Id',
                                    help="Connected Attendance")
    student_id = fields.Many2one('education.student',
                                 string='Student',
                                 help="Student ID for the attendance",required=True
                                 )
 


    student_name = fields.Char(string='Student', related='student_id.name',
                               help="Student name for attendance")
    class_id = fields.Many2one('education.class', string='Class',
                               required=True,
                               help="Enter class for attendance")
    division_id = fields.Many2one('education.class.division',
                                  string='Division',
                                  help="Enter class division for attendance",
                                  required=True)
    date = fields.Date(string='Date', required=True, help="Date of attendance")
    present_morning = fields.Boolean(string='Morning',
                                     help="Enable if the student is present "
                                          "in the morning.")
    present_afternoon = fields.Boolean(string='After Noon',
                                       help="Enable if the student is present "
                                            "in the afternoon")



    full_day_absent = fields.Integer(string='Full Day',
                                     help="Full day present or not")
    half_day_absent = fields.Integer(string='Half Day',
                                     help="Half present or not")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string='State', default='draft',
                             help="Stages of student every day attendance")
    company_id = fields.Many2one(
        'res.company', string='Company', help="Current Company",
        default=lambda self: self.env.company)
    academic_year_id = fields.Many2one('education.academic.year',
                                       string='Academic Year',
                                       related='division_id.academic_year_id',
                                       help="Academic year of education")




    absence_reason = fields.Selection(
        related='permission_id.reason',
        string='Absence Reason',
        store=True,
        readonly=True
    )
    absence_type = fields.Selection(
        related='permission_id.permission_type',
        string='Absence Type',
        store=True,
        readonly=True
    )
    permission_id = fields.Many2one(
        'education.attendance.permission',
        string="Permission Request",
        help="Leave request that justifies this absence.",
        readonly=True,
        copy=False 
    )




    @api.model
    def create(self, vals):
     
        student_id = vals.get('student_id')
        attendance_date = vals.get('date')

        if student_id and attendance_date:
            att_date = fields.Date.from_string(attendance_date)

         
            domain = [
                ('student_id', '=', student_id),
                ('state', '=', 'approved'),
                ('start_date', '<=', fields.Datetime.end_of(att_date, 'day')),
                ('end_date', '>=', fields.Datetime.start_of(att_date, 'day')),
            ]
            permission = self.env['education.attendance.permission'].search(domain, limit=1)

            if permission:
                vals['permission_id'] = permission.id
                
                if permission.permission_type == 'full_day':
                    vals['present_morning'] = False
                    vals['present_afternoon'] = False
                    vals['full_day_absent'] = 1 
                    vals['half_day_absent'] = 0
                else: 
                    vals['present_morning'] = True 
                    vals['present_afternoon'] = False
                    vals['half_day_absent'] = 1 
                    vals['full_day_absent'] = 0
        
        return super(EducationAttendanceLine, self).create(vals)



