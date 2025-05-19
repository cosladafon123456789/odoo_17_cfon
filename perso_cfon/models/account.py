# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    #GAP V1
    is_rebu = fields.Boolean(string=_("Is REBU"), default=False)

    #Not used
    def _set_lot_name(self):
        """"""
        _logger.info("set lot")
        for record in self:           
            stock_move = record.env['stock.move']

            if record.product_id and record.product_id.tracking != 'lot':
                if record.move_id.move_type in ('out_invoice', 'out_refund'):
                    stock_move = record.env['stock.move'].search([('sale_line_id', 'in', record.sale_line_ids.ids)])

                elif record.move_id.move_type in ('in_invoice', 'in_refund'):
                    stock_move = record.env['stock.move'].search([('purchase_line_id', '=', record.purchase_line_id.id)])

                if stock_move and stock_move.lot_ids:
                    _logger.info("los lotes serian")
                    _logger.info(stock_move.lot_ids)


    #GAP V1
    def get_lot_purchase_price(self,lot_values):
        purchase_price = 0
        if lot_values:
            
            for val in lot_values:
                product_id = val.get('product_id', False)

                if self.product_id.id == product_id:
                    lot_id = val.get('lot_id', False)

                    if lot_id:
                        lot = self.env["stock.lot"].browse(int(lot_id))
                        purchase_price = lot.purchase_price

        return purchase_price
    

class AccountMove(models.Model):
    _inherit = 'account.move'

    #GAP V1
    #secondary_entry = fields.Boolean(string=_("Will create REBU entry"), compute="_compute_secondary_entry")
    rebu_entry_id = fields.Many2one("account.move", string=_("REBU Entry"))
    origin_rebu_move_id = fields.Many2one("account.move", string=_("Original Invoice"))
    is_rebu_entry = fields.Boolean(string=_("Is REBU Entry"), default=False)
    rebu_reversal_origin_id = fields.Many2one("account.move", string=_("Original REBU"))
    rebu_reversal_id = fields.Many2one("account.move", string=_("Reversal REBU"))
    is_rebu = fields.Boolean(string=_("Is REBU"), default=False)

    #GAP V1
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)

        for r in res:
            if r.is_rebu and not r.is_rebu_entry:
                for l in r.invoice_line_ids:
                    if l.tax_ids or l.tax_tag_ids:
                        l.write({'tax_ids': [(6, 0, [])], 'tax_tag_ids': [(6, 0, [])]})
                        lines_to_delete = r.line_ids.filtered(lambda x: x.tax_line_id)
                        if lines_to_delete:
                            lines_to_delete.unlink()

        return res


    #GAP V1 : Do not allow write when different rebu products in lines
    def write(self, values):
        result = super().write(values)

        for r in self:
            if r.is_rebu and not r.is_rebu_entry:
                for l in r.invoice_line_ids:
                    if l.tax_ids or l.tax_tag_ids:
                        l.write({'tax_ids': [(6, 0, [])], 'tax_tag_ids': [(6, 0, [])]})
                        lines_to_delete = r.line_ids.filtered(lambda x: x.tax_line_id)
                        if lines_to_delete:
                            lines_to_delete.unlink()

        return result


    #GAP V1 : Return True when there are different rebu products in sale order
    def check_multiple_rebu_products(self):
        self.ensure_one()
        different_rebu = False
        product_lines = self.invoice_line_ids.filtered(lambda x: x.display_type == 'product')

        if product_lines:
            rebu_lines = product_lines.filtered(lambda x: x.is_rebu == True)
            no_rebu_lines = product_lines.filtered(lambda x: x.is_rebu == False)

            if rebu_lines and no_rebu_lines:
                different_rebu = True

        return different_rebu
    
    #GAP V1 : Create REBU Journal Entry. This entry is trigger by rebu product and will only have three account.move.lines
    def create_secondary_entry(self):
        new_entry = False
        rebu_journal = self.company_id.rebu_journal_id

        if rebu_journal:
            new_entry = self.copy({
                'move_type': 'entry',
                'origin_rebu_move_id': self.id,
                'line_ids': [],
                'is_rebu_entry': True,
                'journal_id': rebu_journal.id,
                'ref': self.name,
                'rebu_entry_id': False
            })

            is_refund = False

            mod390_tag = self.env["account.account.tag"].search([('name','=','+mod390[227]')], limit=1)
            mod303_tag = self.env["account.account.tag"].search([('name','=','+mod303[97]')], limit=1)

            if mod390_tag and mod303_tag:
                extra_line_tags = [mod390_tag.id, mod303_tag.id]
            elif not mod390_tag and mod303_tag:
                extra_line_tags = [mod303_tag.id]
            elif mod390_tag and not mod303_tag:
                extra_line_tags = [mod390_tag.id]
            else:
                extra_line_tags = []

            for l in self.line_ids:               
                if l.product_id:
                    entry_lines = []

                    if self.move_type in ('out_invoice', 'in_refund'):
                        line_amount = l.credit
                    if self.move_type in ('in_invoice', 'out_refund'):
                        line_amount = l.debit

                    rebu_tax = l.product_id.rebu_tax_id
                    lot_values = self._get_invoiced_lot_values()
                    purchase_price = l.get_lot_purchase_price(lot_values)
                    margin = line_amount - purchase_price

                    if not rebu_tax:
                        raise UserError(_("Cannot create secondary entry. Missing REBU tax in product"))
                      
                    rebu_amount = margin / (1 + (rebu_tax.amount / 100))
                    margin_tax = margin - rebu_amount

                    repartition_lines = rebu_tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'base')
                    repartition_lines_tax = rebu_tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')
                    
                    if repartition_lines:
                        if repartition_lines.tag_ids:
                            tax_tags = repartition_lines.tag_ids.ids
                        else:
                            tax_tags = []

                    #Primera linea
                    vals_line1 = {
                        'display_type': l.display_type,
                        'currency_id': l.currency_id.id,
                        'move_id': new_entry.id,
                        'account_id': l.account_id.id,
                        'name': "Margen",
                        'date_maturity': l.date_maturity,
                        'discount_date': l.discount_date,
                        'debit': margin,
                    }
                    entry_lines.append(vals_line1)

                    #Segunda linea
                    vals_line2 = {
                        'display_type': l.display_type,
                        'currency_id': l.currency_id.id,
                        'move_id': new_entry.id,
                        'account_id': l.account_id.id,
                        'name': "Base imponible",
                        'date_maturity': l.date_maturity,
                        'discount_date': l.discount_date,
                        'credit': rebu_amount,
                        'tax_tag_ids': tax_tags,
                        'tax_tag_invert': True,
                    }
                    entry_lines.append(vals_line2)

                    #Tercera linea
                    if rebu_tax.invoice_repartition_line_ids:
                        for line in rebu_tax.invoice_repartition_line_ids:
                            if line.account_id:
                                account_id_hac = line.account_id

                    if not account_id_hac:
                        account_id_hac = self.env['account.account'].search([('code', '=', 470001)], limit=1)
                    vals_line3 = {
                        'display_type': 'tax',
                        'currency_id': l.currency_id.id,
                        'move_id': new_entry.id,
                        #477000 Hacienda Pública. IVA repercutido
                        #'account_id': 239,
                        'account_id': account_id_hac.id,
                        'name': rebu_tax.name,
                        'date_maturity': l.date_maturity,
                        'discount_date': l.discount_date,
                        'credit': margin_tax,
                        'tax_tag_ids': repartition_lines_tax.tag_ids.ids,
                        'tax_tag_invert': True,
                    }
                    entry_lines.append(vals_line3)

                    vals_line4 = {
                        'display_type': l.display_type,
                        'currency_id': l.currency_id.id,
                        'move_id': new_entry.id,
                        'account_id': l.account_id.id,
                        'name': "Volumen de operacion",
                        'date_maturity': l.date_maturity,
                        'discount_date': l.discount_date,
                        'debit': l.price_unit - margin_tax,
                        'tax_tag_ids': extra_line_tags,
                        'tax_tag_invert': True,
                    }
                    entry_lines.append(vals_line4)

                    vals_line5 = {
                        'display_type': l.display_type,
                        'currency_id': l.currency_id.id,
                        'move_id': new_entry.id,
                        'account_id': l.account_id.id,
                        'name': "Volumen de operacion",
                        'date_maturity': l.date_maturity,
                        'discount_date': l.discount_date,
                        'credit': l.price_unit - margin_tax,
                        'tax_tag_ids': [],
                    }
                    entry_lines.append(vals_line5)

                    try:
                        self.env["account.move.line"].create(entry_lines)
                        
                    except Exception as e:
                        _logger.info("NO INVOICE LINE CREATION")
                        _logger.info(e)

            if new_entry.line_ids:
                try:
                    new_entry.action_post()

                except Exception as e:
                    _logger.info("NO INVOICE CREATION")
                    _logger.info(e)

        else:
            _logger.info("No REBU Journal configured")

        return new_entry
    
    #GAP V1
    def _get_invoiced_lot_values(self):
        res = super(AccountMove, self)._get_invoiced_lot_values()
        _logger.info(res)

        for val in res:
            lot = val.get('lot_id', False)
            if lot:
                lot_id = self.env["stock.lot"].browse(int(lot))
                val.update({'product_id': lot_id.product_id.id})

        return res

    #GAP V1
    def should_create_secondary_entry(self):
        create_rebu_entry = False
        for r in self:
            if r.move_type == 'out_invoice' and r.is_rebu and not r.is_rebu_entry and not r.rebu_reversal_id:
                create_rebu_entry = True
        
        return create_rebu_entry


    #GAP V1
    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)

        for r in self:
            if r.move_type == 'out_invoice':
                create_rebu_entry = r.should_create_secondary_entry()

                if create_rebu_entry:
                    new_entry = r.create_secondary_entry()
                    if new_entry:
                        r.write({'rebu_entry_id': new_entry.id})

            if r.rebu_reversal_id and r.rebu_reversal_id.state != 'posted':
                r.rebu_reversal_id._post()

        return res
    
    #GAP V1
    def action_open_rebu_entry(self):
        self.ensure_one()

        return {
            'name': _("Journal Entry"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'account.move',
            'res_id': self.rebu_entry_id.id,
            'target': 'current',
        }
    

    #GAP V1
    def action_open_rebu_origin(self):
        self.ensure_one()

        return {
            'name': _("Invoice"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'account.move',
            'res_id': self.origin_rebu_move_id.id,
            'target': 'current',
        }
    

    #GAP V1
    def action_open_reversal_of_rebu(self):
        self.ensure_one()

        return {
            'name': _("REBU Reversal"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'account.move',
            'res_id': self.rebu_reversal_id.id,
            'target': 'current',
        }
    

    #GAP V1
    def action_open_origin_of_rebu_reversal(self):
        self.ensure_one()

        return {
            'name': _("REBU Origin"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'account.move',
            'res_id': self.rebu_reversal_origin_id.id,
            'target': 'current',
        }
    

class AccountAccountTag(models.Model):
    _inherit = 'account.account.tag'

    #GAP V1
    is_rebu = fields.Boolean(string=_("Is REBU tag"), default=False)
