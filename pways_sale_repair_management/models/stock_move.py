from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta
import datetime


class StockMove(models.Model):
    _inherit = 'stock.move'

    date_force_expiry = fields.Date('Expiry Date')

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.depends('product_id', 'picking_type_use_create_lots', 'lot_id.expiration_date')
    def _compute_expiration_date(self):
        for move_line in self:
            if move_line.move_id.date_force_expiry:
                move_line.expiration_date = move_line.move_id.date_force_expiry
            else:
                if not move_line.expiration_date and move_line.lot_id.expiration_date:
                    move_line.expiration_date = move_line.lot_id.expiration_date
                elif move_line.picking_type_use_create_lots:
                    if move_line.product_id.use_expiration_date:
                        if not move_line.expiration_date:
                            move_line.expiration_date = fields.Datetime.today() + datetime.timedelta(days=move_line.product_id.expiration_time)
                    else:
                        move_line.expiration_date = False
