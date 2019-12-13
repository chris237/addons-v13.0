from odoo import fields, api, models
from urllib import urlencode
from urlparse import urljoin



class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_submit(self):
        self.state = 'draft'
        email_template = self.env.ref('ng_double_approval_sale.sales_approval_template')
        group_obj = self.env['res.groups'].search([('name', '=', 'First Sale Approval')])
        print email_template
        print group_obj
        for b in group_obj.users:
            ctx = self.env.context.copy()
            ctx.update({'email_to': b.login, 'doc_link': self._get_url()})
            print "my context", ctx
            print "testing context", ctx['email_to']
            print "the requested email ", b.login
            email_template.with_context(ctx).send_mail(self.id,force_send=False)


    @api.multi
    def action_first_approval(self):
        self.state = 'first_approval'
        email_template = self.env.ref('ng_double_approval_sale.second_sales_approval_template')
        group_obj = self.env['res.groups'].search([('name', '=', 'Second Sale Approval')])
        print "email_template",email_template
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
        email_template = self.env.ref('ng_double_approval_sale.to_confirm_sales_approval_template')
        group_obj = self.env['res.groups'].search([('name', '=', 'Confirm Sale Approval')])
        print "email_template", email_template
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
    def _get_url(self):
        fragment = {}
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        action_id = self.env['ir.model.data'].get_object_reference('sale', 'action_quotations')[1]
        menu_id = self.env['ir.model.data'].get_object_reference('sale', 'menu_sale_quotations')[1]
        fragment['view_type'] = 'form'
        fragment['menu_id'] = menu_id
        fragment['model'] = 'sale.order'
        fragment['id'] = self.id
        fragment['action'] = action_id
        query = {'db': self._cr.dbname}
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res

    partner_id = fields.Many2one('res.partner', string='Customer',
                                 readonly=True, states={'draft': [('readonly', False)],'submit': [('readonly', False)],
                                 'sent': [('readonly', False)]},
                                 required=True, change_default=True,
                                 index=True, track_visibility='always')

    state = fields.Selection([
        ('submit','Draft'),
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='submit')
