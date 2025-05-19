# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    #GAP V1
    rebu_move_ids = fields.Many2many('account.move', 'account_move_reversal_rebu_move', 'reversal_id', 'rebu_move_id', domain=[('state', '=', 'posted')])

    #GAP V1 : include rebu moves
    @api.model
    def default_get(self, fields):
        res = super(AccountMoveReversal, self).default_get(fields)
        move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.env['account.move']

        rebu_moves = []

        for r in move_ids:
            if r.rebu_entry_id:
                rebu_moves.append(r.rebu_entry_id.id)

        if rebu_moves:
            res['rebu_move_ids'] = [(6, 0, rebu_moves)]

        return res

    #GAP V1 : Change journal_id to rebu move journal
    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)

        if move.is_rebu_entry:
            res.update({'journal_id': move.journal_id.id, 'rebu_reversal_origin_id': move.id, 'rebu_reversal_id': False})

        return res

    #GAP V1 : reverse rebu moves as well
    def reverse_moves(self, is_modify=False):
        action = super(AccountMoveReversal,self).reverse_moves(is_modify=is_modify)
        rebu_action = self.reverse_rebu_moves(reversed_moves=action)

        for r in rebu_action:
            r.origin_rebu_move_id.write({'rebu_reversal_id': r.id})

        return action

    def reverse_rebu_moves(self, is_modify=False, reversed_moves=False):
        self.ensure_one()
        rebu_moves_to_reverse = self.rebu_move_ids.filtered(lambda move: move.state == "posted")
        moves = rebu_moves_to_reverse

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = default_vals.get('auto_post') != 'no'
            is_cancel_needed = not is_auto_post and is_modify
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)
            moves._message_log_batch(
                bodies={move.id: _('This entry has been %s', reverse._get_html_link(title=_("reversed"))) for move, reverse in zip(moves, new_moves)}
            )

            if is_modify:
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    rectificativa = self.env["account.move"].search([('reversed_entry_id','=',move.origin_rebu_move_id.id)])
                    moves_vals_list.append(move.copy_data({'date': self.date, 'rebu_reversal_origin_id': move.id, 'is_rebu_entry': True, 'origin_rebu_move_id': rectificativa.id})[0])
                new_moves = self.env['account.move'].create(moves_vals_list)

            moves_to_redirect |= new_moves

        moves_to_redirect

        for m in moves_to_redirect:

            original_move = m.rebu_reversal_origin_id
            
            if original_move:
                original_move.write({'rebu_reversal_id': m.id})

            if self.new_move_ids:

                rebu_tax = False
                for nm in self.new_move_ids:
                    for l in nm.line_ids.filtered(lambda x: x.product_id and x.product_id.rebu_tax_id):
                        rebu_tax = l.product_id.rebu_tax_id

                if rebu_tax:

                    repartition_lines = rebu_tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'base')
                    repartition_lines_tax = rebu_tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')

                    repartition_refund_lines = rebu_tax.refund_repartition_line_ids.filtered(lambda x: x.repartition_type == 'base')
                    repartition_refund_lines_tax = rebu_tax.refund_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')

                    old_tags = False
                    old_tax_tags = False
                    new_tags = False
                    new_tax_tags = False

                    if repartition_lines:
                        if repartition_lines.tag_ids:
                            old_tags = repartition_lines.tag_ids.ids

                    if repartition_lines_tax:
                        if repartition_lines_tax.tag_ids:
                            old_tax_tags = repartition_lines_tax.tag_ids.ids

                    if repartition_refund_lines:
                        if repartition_refund_lines.tag_ids:
                            new_tags = repartition_refund_lines.tag_ids.ids

                    if repartition_refund_lines_tax:
                        if repartition_refund_lines_tax.tag_ids:
                            new_tax_tags = repartition_refund_lines_tax.tag_ids.ids

                    new_tag_ids = []
                    for old_tag in old_tags:
                        new_tag_ids.append((3, old_tag))
                    for new_tag in new_tags:
                        new_tag_ids.append((4, new_tag))

                    new_tax_tag_ids = []
                    for old_tax_tag in old_tax_tags:
                        new_tax_tag_ids.append((3, old_tax_tag))
                    for new_tax_tag in new_tax_tags:
                        new_tax_tag_ids.append((4, new_tax_tag))

                    if new_tag_ids:
                        for ml in m.line_ids.filtered(lambda x: x.name == 'Base imponible'):
                            ml.write({'tax_tag_invert': False, 'tax_tag_ids': new_tag_ids})

                    if new_tax_tag_ids:
                        for ml in m.line_ids.filtered(lambda x: x.name == rebu_tax.name):
                            ml.write({'tax_tag_invert': False, 'tax_tag_ids': new_tax_tag_ids})


                self.new_move_ids.write({'rebu_reversal_id': m.id})

        return moves_to_redirect