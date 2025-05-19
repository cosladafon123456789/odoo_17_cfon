# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)


class StockLot(models.Model):
    _inherit = 'stock.lot'

    #GAP V1
    purchase_price = fields.Float(string=_("Purchase Product Price"))



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    #GAP V1
    def button_validate(self):
        """When picking is validated if picking is incoming then update field purchase_price in lots"""
        res = super(StockPicking, self).button_validate()

        for p in self:
            _logger.info("para cada picking")
            _logger.info(p)
            _logger.info("proviene de un pedido de compra?    : '%s'", str(p.purchase_id))
            if p.picking_type_code == 'incoming' and p.purchase_id:
                purchase_order = p.purchase_id
                _logger.info("es de tipo incoming")
                _logger.info("tiene los movimientos")
                _logger.info(p.move_ids)
                purchase_lines = purchase_order.order_line

                for line in purchase_lines:
                    moves = self.env["stock.move"].search([('purchase_line_id','=',line.id)])

                    for m in moves:
                        for l in m.move_line_ids:
                            _logger.info("tiene lote???     : '%s'", str(l.lot_id))

                            if l.lot_id:
                                purchase_price = line.price_unit

                                _logger.info("precio al que lo ha comprado?")
                                _logger.info(purchase_price)

                                l.lot_id.write({'purchase_price': purchase_price})

        return res

