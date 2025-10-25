from odoo import models, fields, api

class StockLot(models.Model):
    _inherit = 'stock.lot'

    x_bat100 = fields.Boolean(string="Batería 100%")


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_bat100 = fields.Boolean(string="Batería 100%")

    @api.onchange('x_bat100')
    def _onchange_x_bat100(self):
        """Actualizar el lote en tiempo real cuando cambie el toggle."""
        for line in self:
            if line.lot_id:
                line.lot_id.sudo().write({'x_bat100': line.x_bat100})

    @api.model_create_multi
    def create(self, vals_list):
        """Copiar el valor a la creación y actualizar el lote."""
        records = super().create(vals_list)
        for rec in records:
            if rec.lot_id:
                rec.lot_id.sudo().write({'x_bat100': rec.x_bat100})
        return records

    def write(self, vals):
        """Guardar el valor en el lote al editar la línea."""
        res = super().write(vals)
        for rec in self:
            if rec.lot_id and 'x_bat100' in vals:
                rec.lot_id.sudo().write({'x_bat100': vals['x_bat100']})
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """Al validar la transferencia, sincroniza todos los lotes."""
        res = super().button_validate()

        for picking in self:
            for move_line in picking.move_line_ids:
                if move_line.lot_id and move_line.x_bat100:
                    move_line.lot_id.sudo().write({'x_bat100': move_line.x_bat100})

        return res

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    x_bat100 = fields.Boolean(
        string="Batería 100%",
        related='lot_id.x_bat100',
        store=True
    )

