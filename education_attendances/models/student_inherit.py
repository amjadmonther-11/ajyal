from odoo import models, fields, _

class EducationStudentInherit(models.Model):
    _inherit = 'education.student'

    permission_ids = fields.One2many(
        'education.attendance.permission', 'student_id', string='Permissions'
    )

    permission_count = fields.Integer(
        compute='_compute_permission_count', string='Permissions'
    )

    def _compute_permission_count(self):
        for rec in self:
            rec.permission_count = len(rec.permission_ids)

    def action_view_permission_requests(self):
        
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Attendance Permissions'),
            'res_model': 'education.attendance.permission',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }
