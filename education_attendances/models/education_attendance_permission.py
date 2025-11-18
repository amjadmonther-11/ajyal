from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError 
from datetime import datetime, timedelta

class EducationAttendancePermission(models.Model):
    _name = 'education.attendance.permission'
    _description = _('Attendance Permission Request')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    student_id = fields.Many2one(
        'education.student',
        string=_("Student"),
        required=True,
    )

    request_date = fields.Date(
        string=_('Request Date'),
        default=fields.Date.today(),
        required=True,
        tracking=True
    )
    start_date  = fields.Datetime(
        string=_('Start Time'),
        required=True,
        tracking=True
    )
    end_date = fields.Datetime(
        string=_('End Time'),
        required=True,
        tracking=True
    )
    number_of_days = fields.Float(
        string=_('Number of Days'),
        compute='_compute_number_of_days',
        store=True,
        tracking=True
    )
    permission_type = fields.Selection([
        ('early_exit', _('Early Exit')),
        ('partial_absence', _('Partial Absence')),
        ('full_day', _('Full Day Leave')),
    ], string=_("Permission Type"), required=True, tracking=True, default='early_exit')

    reason = fields.Selection([
        ('medical', _('Medical')),
        ('family', _('Family')),
        ('emergency', _('Emergency')),
        ('other', _('Other')),
    ], string=_('Reason'), required=True, tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string=_('Attachments'))

    state = fields.Selection([
        ('new', _('New')),
        ('waiting_approval', _('Waiting Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ], default='new', tracking=True)

    approver_id = fields.Many2one(
        'education.faculty',
        string=_('Employee'),
        required=True,
        tracking=True
    )
    description = fields.Text(string=_('Description/Comments'))
    
    request_no = fields.Char(
        string=_("Permission No."), 
        readonly=True,  
        required=True,
        default='New'
    )

    @api.model
    def create(self, vals):
        if vals.get('request_no', 'New') in (False, 'New'):
            last = self.search([('request_no', 'not in', ('New', False))], order='id desc', limit=1)
            if last and last.request_no:
                last_number = int(last.request_no.replace(_('REQ'), ''))
                new_number = last_number + 1
            else:
                new_number = 1
            vals['request_no'] = _('REQ') + str(new_number).zfill(5)
        return super(EducationAttendancePermission, self).create(vals)

    @api.depends('start_date', 'end_date')
    def _compute_number_of_days(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.number_of_days = delta.days + 1 
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

    


    













