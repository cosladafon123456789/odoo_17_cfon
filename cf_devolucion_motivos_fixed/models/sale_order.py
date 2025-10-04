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
        """Intercepta el botón personalizado 'button_recieved'.
        Abre el wizard salvo que venga con contexto de salto para ejecutar el flujo original.
        """
        self.ensure_one()
        if self.env.context.get('skip_cf_devolucion_motivos'):
            # Ejecuta el flujo original del botón en la superclase
            return super(SaleOrder, self).button_recieved()
        # Abrir wizard
        action = self.env.ref('cf_devolucion_motivos.action_devolucion_wizard').read()[0]
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_sale_order_id': self.id,
        })
        action['context'] = ctx
        return action