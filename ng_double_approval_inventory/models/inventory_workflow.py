from odoo import fields, api, models


class Picking(models.Model):
    _inherit = "stock.picking"
    @api.multi
    def action_first_approval(self):
        self.state = 'first_approval'

    @api.multi
    def action_second_approval(self):
        self.state = 'second_approval'

    state = fields.Selection([
        ('draft', 'Draft'),('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'), ('done', 'Done')], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")
