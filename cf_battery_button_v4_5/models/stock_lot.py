from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_bat100 = fields.Boolean(string="Batería 100%")

    @api.onchange('x_bat100')
    def _onchange_x_bat100(self):
        """Actualizar el lote en tiempo real cuando cambie el toggle."""
        for line in self:
            if line.lot_id:
                line.lot_id.x_bat100 = line.x_bat100

    @api.model_create_multi
    def create(self, vals_list):
        """Copiar el valor a la creación y actualizar el lote."""
        records = super().create(vals_list)
        for rec in records:
            if rec.lot_id:
                rec.lot_id.x_bat100 = rec.x_bat100
        return records

    def write(self, vals):
        """Al validar o editar el movimiento, guardar el valor en el lote."""
        res = super().write(vals)
        for rec in self:
            if rec.lot_id and 'x_bat100' in vals:
                rec.lot_id.write({'x_bat100': vals['x_bat100']})
        return res

    def action_done(self):
        """Forzar sincronización también al validar la transferencia."""
        res = super().action_done()
        for rec in self:
            if rec.lot_id:
                rec.lot_id.x_bat100 = rec.x_bat100
        return res
