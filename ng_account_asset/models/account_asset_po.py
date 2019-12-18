from odoo import api, fields, models, _


class account_move(models.Model):
    _inherit = 'account.move'


    def action_number(self):
        result = super(account_move, self).action_number()
        for inv in self:
            pass
            # self.env['account.move.line'].asset_create(inv.invoice_line)
        return result

    @api.model
    def line_get_convert(self, x, part):
        res = super(account_move, self).line_get_convert(x, part)
        res['asset_id'] = x.get('asset_id', False)
        return res


class purchase(models.Model):
    _inherit = 'purchase.order'


    def button_confirm(self):
        result = super(purchase, self).button_confirm()
        for inv in self:
            self.env['purchase.order.line'].asset_create(inv.order_line)
        return result


class po_line(models.Model):
    _inherit = 'purchase.order.line'

    asset_category_id = fields.Many2one(
        'account.asset.category', string='Asset Category')

    @api.model
    def asset_create(self, lines):
        asset_obj = self.env['account.asset.asset']
        for line in lines:
            if line.asset_category_id:
                vals = {
                    'name': line.name,
                    'code': line.order_id.name or False,
                    'category_id': line.asset_category_id.id,
                    'value': line.price_subtotal,
                    'partner_id': line.order_id.partner_id.id,
                    'company_id': line.order_id.company_id.id,
                    'currency_id': line.order_id.company_id.currency_id.id,
                }
                changed_vals = asset_obj.onchange_category_id(
                    vals['category_id'])
                vals.update(changed_vals['value'])
                asset_id = asset_obj.create(vals)
                if line.asset_category_id.open_asset:
                    asset_id.validate()
        return True