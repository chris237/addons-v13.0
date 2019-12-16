from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError

from urllib.parse import urljoin, urlencode

REQUEST_STAGE = [
    ("draft", "Draft"),
    ("submit", "Department Manager"),
    ("approved", "Main manager"),
    ("warehouse", "Warehouse Officer"),
    ("approval", "Warehouse Manager"),
    ("transfer", "Transfer"),
    ("done", "Done"),
]


class HRDepartment(models.Model):
    """."""

    _inherit = "hr.department"

    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Stock Location",
        domain=lambda self: [
            ("usage", "=", "internal"),
            ("company_id", "=", self.env.user.company_id.id),
        ],
    )


class IRRequest(models.Model):

    _name = "ng.ir.request"
    _inherit = ["mail.thread"]
    _description = "Internal Requisition"
    _order = "state desc, write_date desc"

    def _get_active_login(self):
        """return current logined in user."""
        return self.env.user.id

    def _current_login_employee(self):
        """Get the employee record related to the current login user."""
        hr_employee = self.env["hr.employee"].search(
            [("user_id", "=", self._get_active_login())], limit=1
        )
        return hr_employee.id

    name = fields.Char(string="Number", default="/")
    state = fields.Selection(
        selection=REQUEST_STAGE, default="draft", track_visibility="onchange"
    )
    requester = fields.Many2one(
        comodel_name="res.users",
        string="Requester",
        default=_get_active_login,
        track_visibility="onchange",
    )
    end_user = fields.Many2one(
        comodel_name="hr.employee",
        string="End User",
        default=_current_login_employee,
        required=True,
    )
    request_date = fields.Datetime(
        string="Request Date",
        default=lambda self: datetime.now(),
        help="The day in which request was initiated",
    )
    request_deadline = fields.Datetime(string="Request Deadline")
    hod = fields.Many2one(
        comodel_name="hr.employee", string="H.O.D", domain=[("parent_id", "=", False)]
    )
    department = fields.Many2one(comodel_name="hr.department", string="Department",)
    dst_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination Location",
        help="Departmental Stock Location",
        track_visibility="onchange",
        domain=lambda self: [
            ("usage", "=", "internal"),
            ("company_id", "=", self.env.user.company_id.id),
        ],
    )
    src_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Source Location",
        help="Departmental Stock Location",
        track_visibility="onchange",
        domain=lambda self: [
            ("usage", "=", "internal"),
            ("company_id", "=", self.env.user.company_id.id),
        ],
    )
    request_ids = fields.One2many(
        comodel_name="ng.ir.request.line",
        inverse_name="request_id",
        string="Request Line",
        required=True,
    )
    approve_request_ids = fields.One2many(
        comodel_name="ng.ir.request.approve",
        inverse_name="request_id",
        string="Approved Request Line",
        required=True,
    )
    reason = fields.Text(string="Rejection Reason")
    availaibility = fields.Boolean(
        string="Availaibility", compute="_compute_availabilty"
    )
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env["res.company"]._company_default_get(),
        index=True,
        required=True,
    )

    @api.depends("approve_request_ids")
    def _compute_availabilty(self):
        count_total = len(self.approve_request_ids)
        count_avail = len(
            [
                appr_id.state
                for appr_id in self.approve_request_ids
                if appr_id.state == "available"
            ]
        )
        self.availaibility = count_total == count_avail

    @api.onchange("hod")
    def _onchange_hod(self):
        if self.department:
            if not self.department.location_id:
                raise UserError("Departmental invertory location is not configured")
            self.dst_location_id = self.department.location_id

    @api.model
    def create(self, vals):
        rec_id = super(IRRequest, self).create(vals)
        return rec_id

    def submit(self):
        if not self.request_ids:
            raise UserError("You can not submit an empty item list for requisition.")
        else:
            # fetch email template.
            seq = self.env["ir.sequence"].next_by_code("ng.ir.request")
            recipient = self.recipient("hod", self.hod)
            url = self.request_link()
            mail_template = self.env.ref(
                "ng_internal_requisition.ng_internal_requisition_submit"
            )
            mail_template.with_context({"recipient": recipient, "url": url}).send_mail(
                self.id, force_send=True
            )
            self.write({"state": "submit", "name": seq})

    def department_manager_approve(self):
        if self:
            approved = self.env.context.get("approved")
            if not approved:
                # send rejection mail to the author.
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "ir.request.wizard",
                    "views": [[False, "form"]],
                    "context": {"request_id": self.id},
                    "target": "new",
                }
            else:
                # move to next level and send mail
                url = self.request_link()
                recipient = self.recipient("department_manager", self.department)
                mail_template = self.env.ref(
                    "ng_internal_requisition.ng_internal_requisition_approval"
                )
                mail_template.with_context(
                    {"recipient": recipient, "url": url}
                ).send_mail(self.id, force_send=True)
                self.write({"state": "approved"})

    def main_manager_approve(self):
        approved = self.env.context.get("approved")
        if not approved:
            # send mail to the author.
            return {
                "type": "ir.actions.act_window",
                "res_model": "ir.request.wizard",
                "views": [[False, "form"]],
                "context": {"request_id": self.id},
                "target": "new",
            }
        else:
            # move to next level and send mail
            self.write({"state": "warehouse"})

    def warehouse_officer_confirm(self):
        if not self.approve_request_ids:
            raise UserError(
                "Please add the requested items to the requested items line."
            )
        else:
            url = self.request_link()
            recipient = self.recipient("department_manager", self.department)
            mail_template = self.env.ref(
                "ng_internal_requisition.ng_internal_requisition_warehouse_officer"
            )
            mail_template.with_context({"recipient": recipient, "url": url}).send_mail(
                self.id, force_send=True
            )
            self.write({"state": "approval"})

    def warehouse_officer_confirm_qty(self):
        """Forward the available quantity to warehouse officer."""
        clone = self.copy()
        available_aggregate = sum(
            [approve_request_id.qty for approve_request_id in self.approve_request_ids]
        )
        if available_aggregate <= 0:
            raise UserError(
                "The item line is empty or quantity available can not be forwarded."
            )
            return False
        if self.approve_request_ids and self.request_ids:
            for index, approve_request_id in enumerate(self.approve_request_ids):
                approve_id = approve_request_id.copy()
                availqty, reqqty = approve_id.qty, approve_id.quantity
                if availqty <= reqqty:
                    approve_id.write({"request_id": clone.id, "quantity": availqty})
                    self.approve_request_ids[index].write(
                        {"quantity": reqqty - availqty}
                    )
                else:  # Detach from self record
                    approve_id.sudo().unlink()
            for request_id in self.request_ids:
                req = request_id.copy()
                req.write({"request_id": clone.id})
            clone.write({"state": "approval", "name": self.name})
            if not clone.approve_request_ids:
                clone.sudo().unlink()
                raise UserError(
                    "There is enough quantity available for confirmation, make use of the confirm button."
                )
                return False
            if sum([apr.quantity for apr in self.approve_request_ids]) == 0:
                self.unlink()
            return {
                "type": "ir.actions.act_window",
                "res_model": "ng.ir.request",
                "views": [[False, "form"]],
                "context": {"request_id": self.id},
                "res_id": clone.id,
                "target": "main",
            }
        else:
            raise UserError("No line item(s) defined.")

    def confirmation(self):
        approved = self.env.context.get("approved")
        if not approved:
            # send mail to the author.
            return {
                "type": "ir.actions.act_window",
                "res_model": "ir.request.wizard",
                "views": [[False, "form"]],
                "context": {"request_id": self.id},
                "target": "new",
            }
        else:
            # move to next level and send mail
            self.write({"state": "transfer"})

    def do_transfer(self):
        if self:
            src_location_id = self.src_location_id.id
            dst_location_id = self.dst_location_id.id
            domain = [
                ("active", "=", True),
                ("code", "=", "internal"),
                ("company_id", "=", self.env.user.company_id.id),
            ]
            stock_picking = self.env["stock.picking"]
            picking_type_id = self.env["stock.picking.type"].search(domain, limit=1)
            print(
                domain,
                "**********************************************",
                picking_type_id,
                self.env.user.company_id,
            )
            payload = {
                "location_id": src_location_id,
                "location_dest_id": dst_location_id,
                "picking_type_id": picking_type_id.id,
            }
            stock_picking_id = stock_picking.create(payload)
            move_id = self.stock_move(self.approve_request_ids, stock_picking_id)
            self.process(stock_picking_id)

    def stock_move(self, request_ids, picking_id):
        """."""
        stock_move = self.env["stock.move"]
        for request_id in request_ids:
            payload = {
                "product_id": request_id.product_id.id,
                "name": request_id.product_id.display_name,
                "product_uom_qty": request_id.quantity,
                "product_uom": request_id.uom.id,
                "picking_id": picking_id.id,
                "location_id": picking_id.location_id.id,
                "location_dest_id": picking_id.location_dest_id.id,
            }

            stock_move.create(payload)
            print(payload)
            print(request_id.state)
            request_id.write({"transferred": True})
        self.write({"state": "done"})

    def process(self, picking_id):
        pick_to_do = self.env["stock.picking"]
        pick_to_backorder = self.env["stock.picking"]
        for picking in picking_id:
            # If still in draft => confirm and assign
            if picking.state == "draft":
                picking.action_confirm()
                if picking.state != "assigned":
                    picking.action_assign()
                    if picking.state != "assigned":
                        raise UserError(
                            (
                                "Could not reserve all requested products. Please use the 'Mark as Todo' button to handle the reservation manually."
                            )
                        )
            for move in picking.move_lines:
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            if picking._check_backorder():
                pick_to_backorder |= picking
                continue
            pick_to_do |= picking
        # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
        if pick_to_do:
            pick_to_do.action_done()
            url = self.request_link()
            recipient = self.recipient("department_manager", self.department)
            mail_template = self.env.ref(
                "ng_internal_requisition.ng_internal_requisition_transfer"
            )
            mail_template.with_context({"recipient": recipient, "url": url}).send_mail(
                self.id, force_send=True
            )
        if pick_to_backorder:
            return pick_to_backorder.action_generate_backorder_wizard()
        return False

    def recipient(self, recipient, model):
        """Return recipient email address."""
        if recipient == "hod":
            workmails = model.address_id, model.work_email
            workmail = {workmail for workmail in workmails if workmail}
            workmail = workmail.pop() if workmail else model.work_email
            if not isinstance(workmail, str):
                try:
                    return workmail.email
                except:
                    pass
            return workmail
        elif recipient == "department_manager":
            manager = model.manager_id
            return manager.work_email or manager.address_id.email

    def request_link(self):
        fragment = {}
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        model_data = self.env["ir.model.data"]
        fragment.update(base_url=base_url)
        fragment.update(
            menu_id=model_data.get_object_reference(
                "ng_internal_requisition", "ng_internal_requisition_menu_1"
            )[-1]
        )
        fragment.update(model="ng.ir.request")
        fragment.update(view_type="form")
        fragment.update(
            action=model_data.get_object_reference(
                "ng_internal_requisition", "ng_internal_requisition_action_window"
            )[-1]
        )
        fragment.update(id=self.id)
        query = {"db": self.env.cr.dbname}
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res
