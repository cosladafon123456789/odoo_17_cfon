from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    x_studio_comprado_readonly = fields.Boolean(string="Bloqueo TeComproTuMovil", default=False)

    def write(self, vals):
        if any(rec.x_studio_comprado_readonly for rec in self) and "x_studio_comprado" in vals:
            raise UserError(_("El campo 'Te compro tu móvil' está bloqueado tras el envío del WhatsApp."))
        return super().write(vals)