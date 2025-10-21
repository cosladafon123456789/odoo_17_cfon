from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Flag interno para bloquear edición del check tras envío
    x_studio_comprado_readonly = fields.Boolean(string="Bloqueo TeComproTuMovil", default=False)

    def write(self, vals):
        # Si está bloqueado, impedir cambios en x_studio_comprado (salvo procesos server-side que no lo toquen)
        if any(rec.x_studio_comprado_readonly for rec in self) and "x_studio_comprado" in vals:
            # mantenerlo en True y rechazar cambios
            raise UserError(_("El campo 'Te compro tu móvil' está bloqueado tras el envío del WhatsApp."))
        return super().write(vals)