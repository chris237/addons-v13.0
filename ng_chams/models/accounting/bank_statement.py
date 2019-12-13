from odoo import models, fields, api


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].get('name')
        vals['name'] = sequence

        ctx = self.env.context.copy()
        ctx.update({'journal_code': self.code})

        return super(AccountBankStatement, self).create(vals)

    name = fields.Char(string='Reference', readonly=True)

    code = fields.Char(string="Code", related='journal_id.code')
