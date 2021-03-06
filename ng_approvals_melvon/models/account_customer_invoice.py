from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    state = fields.Selection([
        ('draft', 'Draft'),

        ('submitted', 'Submitted'),

        ('icu_approval', 'ICU Approved'),
        ('coo_approval', 'COO Approved'),
        ('md_approval', 'MD Approved'),

        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' status is used when the invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. "
             "It stays in the open status till the user pays the invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. "
             "Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")

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

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        print self.type
        # if self.type == 'out_invoice':
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft', 'md_approval']):
            raise UserError(
                _("Invoice must be in Draft state in order to validate it."))
        # else:
        # if to_open_invoices.filtered(lambda inv: inv.state not in ['md_approval']):
        #     raise UserError(_("Invoice must be in MD Approval state in order to validate it."))

        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()
