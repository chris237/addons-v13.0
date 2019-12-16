from odoo import api, fields, models, _


class prepayment(models.Model):
    _inherit = 'account.prepayment'

    state = fields.Selection(
        selection=[('draft', 'Draft'),

                   ('submitted', 'Submitted'),

                   ('icu_approval', 'ICU Approved'),
                   ('coo_approval', 'COO Approved'),
                   ('md_approval', 'MD Approved'),

                   ('open', 'Running'),
                   ('close', 'Closed'),
                   ('open1', 'Confirmed'),
                   ('approve', 'Approved'),
                   ('reject', 'Rejected'),
                   ('cancel', 'Cancelled')], string='State',
        required=True,
        help="When an prepayment or Additions is created, the state is 'Draft'.\n"
             "If the prepayment is confirmed, the state goes in 'Running' and the Amortization lines can be posted in the accounting.\n"
             "If the Additions is confirmed, the state goes in 'Confirmed' \n"
             "If the Additions is approved, the state goes in 'Approved' \n"
             "If the Additions is rejected, the state goes in 'Rejected' \n"
             "If the Additions is cancelled, the state goes in 'Cancelled' \n"
             "You can manually close an prepayment when the Amortization is over. If the last line of Amortization is posted, the prepayment automatically goes in that state.", readonly=True, default='draft')

    @api.multi
    def submit(self):
        return self.write({'state': 'submitted'})

    @api.multi
    def return_submit(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_icu_approval(self):
        return self.write({'state': 'icu_approval'})

    @api.multi
    def return_action_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def return_icu_approval(self):
        return self.write({'state': 'icu_approval'})

    @api.multi
    def action_coo_approval(self):
        return self.write({'state': 'coo_approval'})

    @api.multi
    def action_md_approval(self):
        return self.write({'state': 'md_approval'})

    @api.multi
    def return_coo_approval(self):
        return self.write({'state': 'coo_approval'})
