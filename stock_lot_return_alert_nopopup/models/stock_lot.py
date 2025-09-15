
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    return_count = fields.Integer(
        string='Return count (done)',
        compute='_compute_return_count',
        help='Número de recepciones de devolución (done) asociadas a este número de serie/lote.',
        readonly=True,
        store=False,
    )
    needs_review = fields.Boolean(
        string='Needs review (>=2 returns)',
        compute='_compute_return_count',
        help='Marcado si este número de serie/lote acumula 2 o más devoluciones.',
        search='_search_needs_review',
        readonly=True,
        store=False,
    )

    def _search_needs_review(self, operator, value):
        # Soporta ('=', True/False) y ('!=', True/False)
        if operator not in ('=', '!='):
            return []
        domain = [
            ('state', '=', 'done'),
            ('move_id.origin_returned_move_id', '!=', False),
            ('move_id.picking_id.picking_type_code', '=', 'incoming'),
            ('lot_id', '!=', False),
        ]
        groups = self.env['stock.move.line'].sudo().read_group(domain, ['id:count'], ['lot_id'])
        lot_ids = [g['lot_id'][0] for g in groups if g['id_count'] >= 2 and g.get('lot_id')]
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('id', 'in', lot_ids)]
        else:
            return [('id', 'not in', lot_ids)]

    @api.depends('quant_ids', 'quant_ids.quantity')
    def _compute_return_count(self):
        # Calcula por búsqueda cada vez (no almacena).
        for lot in self:
            if not lot.id:
                lot.return_count = 0
                lot.needs_review = False
                continue
            count = self.env['stock.move.line'].sudo().search_count([
                ('lot_id', '=', lot.id),
                ('state', '=', 'done'),
                ('move_id.origin_returned_move_id', '!=', False),
                ('move_id.picking_id.picking_type_code', '=', 'incoming'),
            ])
            lot.return_count = count
            lot.needs_review = count >= 2
