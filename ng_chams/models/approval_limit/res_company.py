# -*- encoding: utf-8 -*-
########################################################################
# I want to make the approval limit configurable in the company settings
# The limits for the ICU and the CFO are set on the company form.
########################################################################

from odoo import fields, models


class Company(models.Model):

    _inherit = 'res.company'

    icu_limit = fields.Float("ICU Limit", help="""Amounts above this limit must go through approvals higher than the 
    ICU's""")

    cfo_limit = fields.Float("CFO Limit", help="""Amounts above this limit must pass through MD's approval""")
