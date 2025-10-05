from odoo import fields, models, api
class SaleOrder(models.Model):
    _inherit = "sale.order"
    fecha_devolucion = fields.Datetime(string="Fecha de devolución", copy=False, tracking=True)
    @api.model
    def cf_safe_backfill_fecha_devolucion(self):
        IrField = self.env['ir.model.fields'].sudo()
        if not IrField.search_count([('model','=','sale.order'),('name','=','motivo_devolucion')]):
            return True
        orders = self.search([('motivo_devolucion','!=',False), ('fecha_devolucion','=',False)], limit=1000)
        now = fields.Datetime.now()
        for o in orders:
            o.fecha_devolucion = now
        return True
