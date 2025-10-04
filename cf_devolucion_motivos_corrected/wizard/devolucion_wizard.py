from odoo import api, fields, models, _
from odoo.exceptions import UserError

class DevolucionWizard(models.TransientModel):
    _name = "cf.devolucion.wizard"
    _description = "Wizard de motivo de devolución"

    sale_order_id = fields.Many2one("sale.order", string="Pedido", required=True, ondelete="cascade")

    motivo = fields.Selection([
        ('bat_85', 'Batería < 85%'),
        ('bat_90_mm', 'Batería < 90% (MediaMarkt)'),
        ('no_como_nuevo', 'No corresponde con estado “Como Nuevo”'),
        ('defectuoso', 'Producto defectuoso'),
        ('dif_descrito', 'Diferente al descrito / modelo equivocado'),
        ('acc_faltantes', 'Accesorios faltantes / incompletos'),
        ('estetico', 'Problema estético (rayado, desgaste, etc.)'),
        ('dup_pedido', 'Pedido duplicado / error del cliente'),
        ('retraso', 'Retraso en la entrega'),
        ('garantia', 'Problema con la garantía'),
        ('otro', 'Otro'),
    ], string="Motivo de devolución", required=True)

    detalle = fields.Text(string="Detalle del motivo")
    tipo_error = fields.Selection([
        ('interno', 'Interno (almacén, control de calidad, anuncio incorrecto)'),
        ('externo', 'Externo (cliente, transporte, garantía fabricante)'),
    ], string="Tipo de error", required=True, default='interno')

    @api.onchange('motivo')
    def _onchange_motivo(self):
        # Limpiar detalle cuando cambie motivo
        if self.motivo not in ('defectuoso', 'acc_faltantes', 'otro'):
            # Mantener detalle opcional para otros motivos, pero no obligatorio
            pass

    def action_confirm(self):
        self.ensure_one()
        order = self.sale_order_id
        # Validaciones de detalle obligatorio para ciertos motivos
        if self.motivo in ('defectuoso', 'acc_faltantes', 'otro'):
            if not (self.detalle or '').strip():
                raise UserError(_("Debes especificar el detalle para el motivo seleccionado."))

        # Guardar en la orden
        order.write({
            'motivo_devolucion': self.motivo,
            'detalle_devolucion': self.detalle if self.motivo in ('defectuoso','acc_faltantes','otro') else (self.detalle or ''),
            'tipo_error_devolucion': self.tipo_error,
        })

        # Continuar con la acción original del botón 'button_recieved'
        # Usamos contexto para saltar nuestro propio override y llamar a super()
        return order.with_context(skip_cf_devolucion_motivos=True).button_recieved()