from datetime import datetime
from odoo import models, fields, api


class IRRequestLine(models.Model):
    _name = "ng.ir.request.line"
    _description = "Requisition Line"

    request_id = fields.Many2one(comodel_name="ng.ir.request", string="Request")
    product_id = fields.Char(string="Product")
    quantity = fields.Float(string="Quantity", default=1.0)
    uom = fields.Many2one(comodel_name="uom.uom", string="U.O.M")


class IRRequestApprove(models.Model):
    _name = "ng.ir.request.approve"
    _description = "Approved Requisition"

    STATE = [
        ("not_available", "Not Available"),
        ("partially_available", "Partially Available"),
        ("available", "Available"),
        ("awaiting", "Awaiting Availability"),
    ]

    request_id = fields.Many2one(comodel_name="ng.ir.request", string="Request")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    quantity = fields.Float(string="Quantity", default=1.0)
    uom = fields.Many2one(comodel_name="uom.uom", string="U.O.M")
    qty = fields.Float(string="Qty Available", compute="_compute_qty")
    state = fields.Selection(
        selection=STATE, string="State", compute="_compute_state", store=False
    )
    purchase_agreement = fields.Char(string="Purchase Agreement")
    to_procure = fields.Boolean(string="To Procure", compute="_compute_to_procure")
    transferred = fields.Boolean(string="Transferred", default=False)

    @api.depends("state")
    def _compute_to_procure(self):
        to_procure = (
            self.state == "partially_available" or self.state == "not_available"
        )
        if self.purchase_agreement:
            self.to_procure = False
        else:
            self.to_procure = to_procure

    @api.depends("product_id")
    def _compute_qty(self):
        location_id = self.request_id.src_location_id.id
        product_id = self.product_id.id
        stock_quants = self.env["stock.quant"].search(
            [("location_id", "=", location_id), ("product_id", "=", product_id)]
        )
        self.qty = sum([stock_quant.quantity for stock_quant in stock_quants])

    @api.depends("qty")
    def _compute_state(self):
        if self.qty <= 0:
            self.state = "not_available"
        elif self.qty > 0 and self.qty < self.quantity:
            self.state = "partially_available"
        else:
            self.state = "available"

    def procure(self):
        product_id, quantity = self.product_id, self.quantity - self.qty
        requisition = self.env["purchase.requisition"]
        line = self.env["purchase.requisition.line"]
        request_identity = self.request_id.name
        requisition_id = requisition.create({"name": "/"})
        payload = {
            "product_id": product_id.id,
            "product_uom_id": product_id.uom_id.id,
            "product_qty": quantity,
            "qty_ordered": quantity,
            "requisition_id": requisition_id.id,
            "price_unit": product_id.standard_price,
        }
        line.create(payload)
        self.purchase_agreement = requisition_id.name
        # Rename the purchase requestion name to ref
        origin = "{}/{}".format(request_identity, requisition_id.name)
        requisition_id.write({"name": origin})
