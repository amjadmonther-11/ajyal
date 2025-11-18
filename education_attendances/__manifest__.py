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
{
    'name': 'Educational Attendance Management',
    'version': '17.0',
    'summary': """Opener to Student Attendance Management System for Educational ERP""",
    'description': 'An easy and efficient management tool to manage and track student'
                   ' attendance. Enables different types of filtration to generate '
                   'the adequate reports',
    'category': 'Industries',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "http://www.educationalerp.com",
    'depends': ['education_core'],
    'data': [

        'security/ir.model.access.csv',
        'views/students_attendance.xml',
        'views/student_view.xml',
        'views/education_attendance_permission_views.xml',
        'views/student_inherit_view.xml',
         # 'views/dashboard_views.xml',
    ],
    # 'assets': {
      # 'web.assets_backend': [
        #   'education_attendances/static/src/js/attendance_dashboard.js',
          # 'education_attendances/static/src/css/attendance_dashboard.css',
          # 'education_attendances/static/src/css/attendance.css',
      # ],  
    # },
    # 'qweb': ["static/src/xml/attendance_dashboard.xml"],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
