from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    state = fields.Selection([
        ('draft', 'Draft'),

        ('submitted', 'Submitted'),

        ('icu_approval', 'ICU Approved'),
        ('coo_approval', 'COO Approved'),
        ('md_approval', 'MD Approved'),

        ('cancel', 'Cancelled'),
        ('proforma', 'Pro-forma'),
        ('posted', 'Posted')
    ], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.")

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
