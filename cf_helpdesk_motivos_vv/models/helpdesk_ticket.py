from odoo import models, fields
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    motivo_devolucion = fields.Selection([
        ('desistimiento', 'Desistimiento (21 días)'),
        ('bateria', 'Problema de batería'),
        ('pantalla', 'Problema de pantalla/display'),
        ('camara', 'Problema de cámara/componentes'),
        ('carga', 'Problema de carga/accesorios'),
        ('software', 'Problema de sistema/software'),
        ('no_conforme', 'Producto no conforme con lo anunciado'),
        ('garantia', 'Tramitación de garantía'),
        ('otros', 'Otros'),
    ], string="Motivo de devolución")

    def write(self, vals):
        res = super().write(vals)
        etapas_requieren_motivo = ["Devolución aceptada", "Reembolsado", "Devolución rechazada"]
        for ticket in self:
            if ticket.stage_id and ticket.stage_id.name in etapas_requieren_motivo:
                if not ticket.motivo_devolucion:
                    raise ValidationError(
                        f"Debe indicar un motivo de devolución antes de mover el ticket a la etapa '{ticket.stage_id.name}'."
                    )
        return res
