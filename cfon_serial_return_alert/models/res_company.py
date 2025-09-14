
# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    return_alert_threshold = fields.Integer(
        string="Serial Return Alert Threshold",
        default=2,
        help="How many Customer → Internal returns for the same serial/lot before raising an alert."
    )
    return_alert_responsible_id = fields.Many2one(
        "res.users",
        string="Return Alerts Responsible",
        help="User to assign activities to. If empty, the activity is unassigned."
    )

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    return_alert_threshold = fields.Integer(related="company_id.return_alert_threshold", readonly=False)
    return_alert_responsible_id = fields.Many2one(related="company_id.return_alert_responsible_id", readonly=False)
