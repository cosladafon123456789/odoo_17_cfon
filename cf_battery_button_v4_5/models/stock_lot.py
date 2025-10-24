from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Campo espejo (no guardado, pero editable)
    x_bat100 = fields.Boolean(string="Batería 100%")

    @api.onchange('x_bat100')
    def _onchange_x_bat100(self):
        """Si cambia el toggle en el popup, se guarda directamente en el lote."""
        for line in self:
            if line.lot_id:
                line.lot_id.x_bat100 = line.x_bat100

    @api.model_create_multi
    def create(self, vals_list):
        """Cuando se crea una línea nueva, replicar el valor al lote."""
        records = super().create(vals_list)
        for rec in records:
            if rec.lot_id:
                rec.lot_id.x_bat100 = rec.x_bat100
        return records

    def write(self, vals):
        """Cuando se escribe (por validación), actualizar el lote."""
        res = super().write(vals)
        for rec in self:
            if rec.lot_id and 'x_bat100' in vals:
                rec.lot_id.x_bat100 = vals['x_bat100']
        return res
