from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    motivo_devolucion = fields.Selection([
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
    ], string="Motivo de devolución", tracking=True)

    detalle_devolucion = fields.Text(string="Detalle del motivo", tracking=True)
    tipo_error_devolucion = fields.Selection([
        ('interno', 'Interno (almacén, control de calidad, anuncio incorrecto)'),
        ('externo', 'Externo (cliente, transporte, garantía fabricante)'),
    ], string="Tipo de error", tracking=True)

    def button_recieved(self):
        """Abre el wizard al pulsar 'Recibido'. Si viene del wizard, ejecuta el flujo original sin super()."""
        self.ensure_one()

        # Si viene del wizard: ejecutar el flujo original del módulo externo directamente
        if self.env.context.get('from_wizard'):
            # Llamada directa a la acción original (del módulo pways_sale_repair_management)
            # Simula pulsar el botón sin reabrir el wizard
            return self.with_context(skip_wizard=True)._button_recieved_original()

        # En cualquier otro caso, abrir el wizard
        try:
            action = self.env.ref('cf_forzar_wizard_devolucion.action_devolucion_wizard').read()[0]
        except ValueError:
            action = self.env.ref('cf_devolucion_motivos_corrected.action_devolucion_wizard').read()[0]

        ctx = dict(self.env.context or {})
        ctx.update({'default_sale_order_id': self.id})
        action['context'] = ctx
        return action

    def _button_recieved_original(self):
        """Lógica del botón original del módulo pways_sale_repair_management."""
        # ⚠️ IMPORTANTE: aquí puedes copiar lo que hacía originalmente el método button_recieved del otro módulo.
        # Si no lo sabes exactamente, al menos dejamos un marcador:
        if hasattr(super(SaleOrder, self), 'button_recieved'):
            return super(SaleOrder, self).button_recieved()
        else:
            raise UserError(_("No se pudo ejecutar el método original de 'Recibido'."))
