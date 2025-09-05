# ©  2023-now Terrabit
# See README.rst file on addons root folder for license details

from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    send_cancel_mail = fields.Boolean(
        string="Send an e-mail when a sale order cancel is requested",
        readonly=False,
        config_parameter="sale_cancel_order.default_email_send",
    )
    send_cancel_mail_to = fields.Many2many("res.partner", string="Send mail to salesperson and")

    def set_values(self):
        res = super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_cancel_order.default_email_to", self.send_cancel_mail_to.ids
        )
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        partner_ids = self.env["ir.config_parameter"].sudo().get_param("sale_cancel_order.default_email_to")
        res.update(
            send_cancel_mail_to=[(6, 0, literal_eval(partner_ids))] if partner_ids else False,
        )
        return res
