from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class account_payment(models.Model):
    _inherit = "account.payment"

    state = fields.Selection([('draft', 'Draft'),

                              ('icu_approval', 'ICU Approved'),
                              ('coo_approval', 'COO Approved'),
                              ('md_approval', 'MD Approved'),

                              ('posted', 'Posted'),
                              ('sent', 'Sent'),
                              ('reconciled', 'Reconciled')],
                             readonly=True, default='draft', copy=False, string="Status")

    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            # if rec.state != 'md_approval':
            #     raise UserError(
            #         _("Only a MD Approval payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(
                    _("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                sequence_code)

            # Create the journal entry
            amount = rec.amount * \
                (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(
                    lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})

    # state = fields.Selection([('start_process', 'Draft'),
    #
    #                           ('icu_approval', 'ICU Approval'),
    #                           ('coo_approval', 'COO Approval'),
    #                           ('draft', 'MD Approval'),
    #
    #                           ('posted', 'Posted'),
    #                           ('sent', 'Sent'),
    #                           ('reconciled', 'Reconciled')], readonly=True, default='start_process', copy=False, string="Status")

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
