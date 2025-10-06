from odoo import api, fields, models, _

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
        """Abre el wizard siempre, salvo cuando viene del wizard."""
        self.ensure_one()

        # Si viene del wizard (ya se rellenó el motivo), ejecutar la acción real
        if self.env.context.get('from_wizard'):
            # 🔹 Acción original del botón "Recibido"
            # Aquí puedes ajustar lo que haga normalmente tu botón (por ejemplo cambiar estado)
            self.state = 'done'
            return True

        # En cualquier otro caso, abrir el wizard
        action = self.env.ref('cf_forzar_wizard_devolucion.action_devolucion_wizard').read()[0]
        ctx = dict(self.env.context or {})
        ctx.update({'default_sale_order_id': self.id})
        action['context'] = ctx
        return action
