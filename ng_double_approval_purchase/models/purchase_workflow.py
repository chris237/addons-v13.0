from odoo import fields, api, models
from urllib import urlencode
from urlparse import urljoin

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent','first_approval','second_approval']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id.compute(
                        order.company_id.po_double_validation_amount, order.currency_id)) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True

    @api.multi
    def action_submit(self):
        self.state = 'sent'
        email_template = self.env.ref('ng_double_approval_purchase.purchase_approval_template')
        group_obj = self.env['res.groups'].search([('name', '=', 'First Purchase Approval')])
        print email_template
        print group_obj
        for b in group_obj.users:
            ctx = self.env.context.copy()
            ctx.update({'email_to': b.login, 'doc_link': self._get_url() })
            print "my context", ctx
            print "testing context", ctx['email_to']
            print "the requested email ", b.login
            email_template.with_context(ctx).send_mail(self.id, force_send=False)

    @api.multi
    def action_first_approval(self):
        self.state = 'first_approval'
        email_template = self.env.ref('ng_double_approval_purchase.purchase_approval_template')
        group_obj = self.env['res.groups'].search([('name', '=', 'Second Purchase Approval')])
        print email_template
        print group_obj
        for b in group_obj.users:
            ctx = self.env.context.copy()
            ctx.update({'email_to': b.login, 'doc_link': self._get_url()})
            print "my context", ctx
            print "testing context", ctx['email_to']
            print "the requested email ", b.login
            email_template.with_context(ctx).send_mail(self.id, force_send=False)

    @api.multi
    def action_second_approval(self):
        self.state = 'second_approval'
        email_template = self.env.ref('ng_double_approval_purchase.purchase_approval_template')
        group_obj = self.env['res.groups'].search([('name', '=', 'First Purchase Approval')])
        print email_template
        print group_obj
        for b in group_obj.users:
            ctx = self.env.context.copy()
            ctx.update({'email_to': b.login, 'doc_link': self._get_url() })
            print "my context", ctx
            print "testing context", ctx['email_to']
            print "the requested email ", b.login
            email_template.with_context(ctx).send_mail(self.id, force_send=False)


    @api.multi
    def _get_url(self):
        fragment = {}
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        action_id = self.env['ir.model.data'].get_object_reference('purchase', 'purchase_form_action')[1]
        menu_id = self.env['ir.model.data'].get_object_reference('purchase', 'menu_purchase_form_action')[1]
        fragment['view_type'] = 'form'
        fragment['menu_id'] = menu_id
        fragment['model'] = 'purchase.order'
        fragment['id'] = self.id
        fragment['action'] = action_id
        query = {'db': self._cr.dbname}
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res

    state = fields.Selection([
        ('submit','Submit'),
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='submit', track_visibility='onchange')

