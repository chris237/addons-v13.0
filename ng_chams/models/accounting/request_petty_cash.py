from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class RequestPettyCash(models.Model):
    _name = 'request.petty.cash'

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].get('name')
        vals['name'] = sequence
        return super(RequestPettyCash, self).create(vals)

    name = fields.Char(string="Request Id", readonly=True)
    request_label = fields.Char(string="Request Label")
    bank_statement = fields.Many2one('account.bank.statement', string="Bank Statement")

    location = fields.Many2one('request.location', string="Location")

    cash_limit = fields.Float(string="Cash Limit", compute='onchange_limit')

    petty_cashier = fields.Many2one('res.partner', string="Petty Cashier", required=True)
    petty_cash_amount = fields.Float(string="Petty Cash Amount")
    requested_date = fields.Date(string="Requested Date")
    approved_date = fields.Date(string="Approved Date")
    approval_manager = fields.Many2one('res.partner', string="Approval Manager")

    state = fields.Selection([('applicant', 'New'),

                              ('submitted', 'Submitted'),

                              ('department', 'Department Approved'),

                              ('icu', 'ICU Approved'),
                              ('finance', 'Finance Approved'),
                              ('done', 'Done')], default='applicant')

    @api.model
    @api.depends('location')
    def onchange_limit(self):
        if self.location:
            self.cash_limit = self.location.location_limit

    @api.multi
    def submit(self):
        if self.petty_cash_amount > self.cash_limit:
            raise UserError(_("Limit Exceeded."))
        else:
            return self.write({'state': 'submitted'})

    @api.multi
    def dept_approval(self):
        return self.write({'state': 'department'})

    @api.multi
    def return_submit(self):
        return self.write({'state': 'applicant'})

    @api.multi
    def return_dept(self):
        return self.write({'state': 'department'})

    @api.multi
    def icu_approval(self):
        return self.write({'state': 'icu'})

    @api.multi
    def finance_approval(self):
        return self.write({'state': 'finance'})

    @api.multi
    def send_back_icu(self):
        return self.write({'state': 'icu'})

    @api.multi
    def done(self):
        self.approval_manager = self.env.uid
        self.approved_date = datetime.now()

        get_statement = self.env['account.bank.statement'].search(
            [('name', '=', self.bank_statement.name)])
        get_statement.line_ids.create({
            'name': self.request_label,
            'partner_id': self.petty_cashier.id,
            'amount': self.petty_cash_amount,
            'statement_id': get_statement.id,
            'journal_id': get_statement.journal_id.id
        })

        self.location.location_limit -= self.petty_cash_amount
        return self.write({'state': 'done'})

    @api.multi
    def return_new(self):
        return self.write({'state': 'icu'})










