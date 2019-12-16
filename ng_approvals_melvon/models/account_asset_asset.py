from odoo import models, fields, api, _


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

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
        help="When an asset or Additions is created, the state is 'Draft'.\n"
             "If the asset is confirmed, the state goes in 'Running' and the depreciation lines can be posted in the accounting.\n"
             "If the Additions is confirmed, the state goes in 'Confirmed' \n"
             "If the Additions is approved, the state goes in 'Approved' \n"
             "If the Additions is rejected, the state goes in 'Rejected' \n"
             "If the Additions is cancelled, the state goes in 'Cancelled' \n"
             "You can manually close an asset when the depreciation is over. If the last line of depreciation is posted, the asset automatically goes in that state.", readonly=True)

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
