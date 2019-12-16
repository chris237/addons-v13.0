from odoo import models, fields, api, _
from odoo.exceptions import UserError
from urllib.parse import urljoin, urlencode


class ng_leave_approval(models.Model):
    _inherit = 'hr.leave'

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Mgr Approved'),
        ('validate', 'Approved')
    ], default='draft')
    reliever_id = fields.Many2one(
        "hr.employee", string="Reliever", domain="[('id', '!=', employee_id)]")

    def build_url(self):
        """Method to return the url to access the current record."""
        fragment = {}
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        action_id = self.env['ir.model.data'].get_object_reference(
            'hr_holidays', 'hr_leave_action_my')[1]
        menu_id = self.env['ir.model.data'].get_object_reference(
            'hr_holidays', 'hr_leave_menu_my')[1]
        fragment['view_type'] = 'form'
        fragment['menu_id'] = menu_id
        fragment['model'] = 'hr.leave'
        fragment['id'] = self.id
        fragment['action'] = action_id
        query = {'db': self._cr.dbname}
        res = urljoin(base_url + "/web", "?%s#%s" %
                      (urlencode(query), urlencode(fragment)))
        return res

    def send_message(self, template, mail_context):
        """Method called to send email to the valid recipients."""
        recipients = mail_context.get('recipient')
        for recipient in recipients:
            mail_context['recipient'] = recipient
            try:
                template.with_context(mail_context).send_mail(self.id, force_send=True)
            except:
                continue

    def _prepare_mail_values(self, recipient, template):
        """Prepare the values to pass along in the email"""
        sender = self.env['hr.employee'].sudo().search(
            [('user_id', '=', self.env.uid)], limit=1)
        url = self.build_url()
        mail_context = self._context.copy()
        mail_context.update(
            {'recipient': recipient, 'sender': sender, 'url': url})
        return template, mail_context

    def action_confirm(self):
        """Method to submit leave request for approval and trigger an email notification to
        the department manager or employee's manager with a link to the leave request."""
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(
                _('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        employee = self.employee_id
        mgr = employee.parent_id
        dept_mgr = employee.parent_id
        recipient = dept_mgr or mgr if employee != dept_mgr else mgr
        template = self.env.ref(
            "ng_leave_approval.email_template_leave_request", False)
        template, mail_context = self._prepare_mail_values(recipient, template)
        if self.holiday_type == 'employee':
            self.send_message(template, mail_context)
        return self.sudo().write({'state': 'confirm'})

    def action_approve(self):
        self.ensure_one()
        """
        if double_validation: this method is the first approval
        if not double_validation: this method calls action_validate() below
        """
        if self.holiday_status_id.double_validation:
            if self.env.user == self.employee_id.user_id:
                raise UserError(
                    _("You are not allowed to approve your own request!"))
        manager = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        if self.state != 'confirm':
            raise UserError(
                _('Leave request must be confirmed ("To Approve") in order to approve it.'))

        if self.holiday_status_id.double_validation:
            hr_managers = self.env.ref('hr.group_hr_manager').users
            rel_employees = self.env['hr.employee'].sudo().search(
                [('user_id', 'in', hr_managers.ids)])
            template = self.env.ref(
                "ng_leave_approval.employee_manager_approve", False)
            template, mail_context = self.sudo()._prepare_mail_values(rel_employees, template)
            if self.holiday_type == 'employee':
                self.send_message(template, mail_context)
                mail_context['recipient'] = self.employee_id
                template = self.env.ref('ng_leave_approval.leave_request_await_hr_approval')
                self.send_message(template, mail_context)
            # TODO: Extend method to cater for employee batch
            # #elseif self.holiday_type == 'employee_batch'
            return self.sudo().write({'state': 'validate1', 'manager_id': manager.id if manager else False})
        else:
            recipient = self.employee_id
            template = self.env.ref(
                "ng_leave_approval.email_template_leave_request_approve", False)
            template, mail_context = self._prepare_mail_values(
                recipient, template)
            if self.holiday_type == 'employee':
                self.send_message(template, mail_context)
            # TODO: Extend the method for employee batch
            # elseif self.holiday_type == 'employee_batch'
            return self.sudo().action_validate()

    def action_validate(self):
        self.ensure_one()
        """Method to approve leave request. Accepts self as argument."""
        if self.holiday_type == 'employee':
            if self.env.user == self.employee_id.user_id:
                raise UserError(
                    _("You are not allowed to approve your own request!"))
            recipient = self.employee_id
            template = self.env.ref(
                "ng_leave_approval.email_template_leave_request_approve", False)
            template, mail_context = self._prepare_mail_values(
                recipient, template)
            self.send_message(template, mail_context)
        return super(ng_leave_approval, self).action_validate()
