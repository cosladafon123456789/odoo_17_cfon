from odoo import models, fields, api

class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    bat100 = fields.Boolean(string='BAT100', tracking=True)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    bat100 = fields.Boolean(string='BAT100', tracking=True)

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        for line in self:
            if line.lot_id:
                line.bat100 = line.lot_id.bat100

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.lot_id:
                line.lot_id.write({'bat100': line.bat100})
        return lines

    def write(self, vals):
        res = super().write(vals)
        if 'bat100' in vals:
            for line in self:
                if line.lot_id:
                    line.lot_id.write({'bat100': vals['bat100']})
        return res
