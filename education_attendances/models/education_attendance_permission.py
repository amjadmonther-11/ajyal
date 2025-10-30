from odoo import models, fields,api,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class EducationAttendancePermission(models.Model):
    _name = 'education.attendance.permission'
    _description = 'Attendance Permission Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    
    student_id = fields.Many2one(
        'education.student',
        string="Student",
        required=True,
       
        )



    request_date = fields.Date(string='Request Date', default=fields.Date.today(), required=True, tracking=True)
    start_date  = fields.Datetime(string='Start Time', required=True, tracking=True)
    end_date = fields.Datetime(string='End Time', required=True, tracking=True)
    number_of_days = fields.Float(string='Number of Days', compute='_compute_number_of_days', store=True, tracking=True)
    permission_type = fields.Selection([
        ('early_exit', 'Early Exit'),
        ('partial_absence', 'Partial Absence'),
        ('full_day', 'Full Day Leave'),
    ], string="Permission Type", required=True, tracking=True,default='early_exit')
    reason = fields.Selection([
        ('medical', 'Medical'),
        ('family', 'Family'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    ], string='Reason', required=True, tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    state = fields.Selection([
        ('new', 'New'),
        ('waiting_approval', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='new', tracking=True)

    approver_id = fields.Many2one('education.faculty', string='Employee', required=True, tracking=True)
    description = fields.Text(string='Description/Comments')
    request_no = fields.Char(
        string="Permission No.", 
        readonly=True,
        copy=False,
        default=lambda self: _('New')
        )


    # absence_type = fields.Char(string='Absence type')
    # absence_reason = fields.Char(string='Absence Reason')



    @api.model
    def create(self, vals):
        if vals.get('request_no', _('New')) == _('New'):
            vals['request_no'] = self.env['ir.sequence'].next_by_code('hr.attendance.permission') or _('New')
        return super(EducationAttendancePermission, self).create(vals)
        return result


    @api.depends('start_date', 'end_date')
    def _compute_number_of_days(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.number_of_days = delta.days+1 
            else:
                record.number_of_days = 0.0


 
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('The start date/time cannot be after the end date/time.'))


    def action_submit_approval(self):
        for record in self:
            record.state = 'waiting_approval'

    def action_approve(self):
        for record in self:
            record.state = 'approved'


    def action_reject(self):
        for record in self:
            record.state = 'rejected'

    def action_reset_to_new(self):
        for record in self:
            record.state = 'new'

    


    













