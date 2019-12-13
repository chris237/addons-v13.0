from odoo import models, fields, api, _


class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"

    state = fields.Selection([
        ('draft', 'Draft'),

        ('submitted', 'Submitted'),

        ('icu_approval', 'ICU Approved'),
        ('coo_approval', 'COO Approved'),
        ('md_approval', 'MD Approved'),

        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')

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
