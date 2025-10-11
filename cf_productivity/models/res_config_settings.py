from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    picking_user_ids = fields.Many2many("res.users", string="Usuarios de pedidos a contabilizar")
    repair_user_ids = fields.Many2many("res.users", string="Usuarios técnicos a contabilizar")
    helpdesk_user_ids = fields.Many2many("res.users", string="Usuarios de postventa a contabilizar")
    send_daily_summary = fields.Boolean("Enviar resumen diario por email", default=True)
    summary_recipient_ids = fields.Many2many("res.users", string="Destinatarios del resumen diario")

    @api.model
    def get_values(self):
        res = super().get_values()
        settings = self.env["cf.productivity.settings"].sudo().search([], limit=1)
        if settings:
            res.update({
                "picking_user_ids": [(6, 0, settings.picking_user_ids.ids)],
                "repair_user_ids": [(6, 0, settings.repair_user_ids.ids)],
                "helpdesk_user_ids": [(6, 0, settings.helpdesk_user_ids.ids)],
                "send_daily_summary": settings.send_daily_summary,
                "summary_recipient_ids": [(6, 0, settings.summary_recipient_ids.ids)]
            })
        return res

    def set_values(self):
        super().set_values()
        settings = self.env["cf.productivity.settings"].sudo().search([], limit=1)
        if not settings:
            settings = self.env["cf.productivity.settings"].sudo().create({})
        settings.write({
            "picking_user_ids": [(6, 0, self.picking_user_ids.ids)],
            "repair_user_ids": [(6, 0, self.repair_user_ids.ids)],
            "helpdesk_user_ids": [(6, 0, self.helpdesk_user_ids.ids)],
            "send_daily_summary": self.send_daily_summary,
            "summary_recipient_ids": [(6, 0, self.summary_recipient_ids.ids)]
        })
