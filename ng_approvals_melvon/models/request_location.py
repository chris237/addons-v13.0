from odoo import models, fields, api
from datetime import datetime, timedelta


class RequestLocation(models.Model):
    _name = 'request.location'

    name = fields.Char(string="Location Name")

    location_limit = fields.Float(string="Request Limit")
