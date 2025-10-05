from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Siempre existe y no rompe aunque no haya otros módulos
    fecha_devolucion = fields.Datetime(string="Fecha de devolución", copy=False, tracking=True)

    @api.model
    def cf_safe_backfill_fecha_devolucion(self):
        """Cron seguro:
        - Si existen los campos de motivos y hay pedidos con motivo pero sin fecha_devolucion -> poner ahora()
        - Si no existen, no hace nada.
        """
        # Comprobamos existencia de 'motivo_devolucion'
        field_exists = self.env['ir.model.fields'].sudo().search_count([
            ('model', '=', 'sale.order'),
            ('name', '=', 'motivo_devolucion')
        ]) > 0
        if not field_exists:
            return True
        orders = self.search([('motivo_devolucion','!=',False), ('fecha_devolucion','=',False)], limit=500)
        now = fields.Datetime.now()
        for o in orders:
            o.fecha_devolucion = now
        return True