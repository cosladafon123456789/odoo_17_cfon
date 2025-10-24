# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CFSerialImportWizard(models.TransientModel):
    _name = "cf.serial.import.wizard"
    _description = "Importación de Números de Serie (IMEI) al Picking con validación en WH/Stock"

    picking_id = fields.Many2one("stock.picking", string="Albarán", required=True, ondelete="cascade")
    imei_text = fields.Text(string="IMEIs / Números de serie (uno por línea)", required=True)
    result_log = fields.Text(string="Resultado", readonly=True)

    def _get_wh_stock_location(self):
        # Buscar ubicación por complete_name exacto 'WH/Stock'
        location = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')], limit=1)
        if not location:
            # Fallback: buscar por name 'Stock' dentro del WH
            location = self.env['stock.location'].search([('name', '=', 'Stock')], limit=1)
        return location

    def _clean_lines(self, text):
        vals = []
        for line in (text or "").splitlines():
            s = (line or "").strip()
            if not s:
                continue
            # quitar espacios internos accidentales
            s = s.replace(" ", "")
            # solo permitir dígitos y letras (algunos SN pueden tener letras)
            # filtrar caracteres raros
            s = "".join(ch for ch in s if ch.isalnum())
            if s:
                vals.append(s)
        # mantener orden pero quitar duplicados
        seen = set()
        out = []
        for v in vals:
            if v in seen:
                continue
            seen.add(v)
            out.append(v)
        return out

    def action_process(self):
        self.ensure_one()
        picking = self.picking_id
        if picking.state in ("done", "cancel"):
            raise UserError(_("No se puede importar en un albarán validado o cancelado."))

        loc_src = self._get_wh_stock_location()
        if not loc_src:
            raise UserError(_("No se encontró la ubicación 'WH/Stock'. Revise la configuración o ajuste el módulo."))

        processed, ignored, not_found, not_in_wh, duplicated = [], [], [], [], []

        lines = self._clean_lines(self.imei_text)
        if not lines:
            raise UserError(_("No se han introducido números de serie válidos."))

        Quant = self.env["stock.quant"]
        Lot = self.env["stock.lot"]
        Move = self.env["stock.move"]
        MoveLine = self.env["stock.move.line"]

        for imei in lines:
            # 1) Debe existir como lot/serial
            lot = Lot.search([("name", "=", imei)], limit=1)
            if not lot:
                not_found.append(imei)
                continue

            # 2) Debe estar con stock disponible en WH/Stock (misma compañía del picking si procede)
            domain_quant = [
                ("lot_id", "=", lot.id),
                ("location_id", "=", loc_src.id),
            ]
            if picking.company_id:
                domain_quant.append(("company_id", "=", picking.company_id.id))

            quants = Quant.search(domain_quant)
            available = 0.0
            for q in quants:
                available += max(q.quantity - q.reserved_quantity, 0.0)

            if available <= 0:
                not_in_wh.append(imei)
                continue

            # 3) Evitar duplicados en otros pickings ya preparados
            mls = MoveLine.search([("lot_id", "=", lot.id), ("picking_id", "!=", picking.id), ("state", "!=", "cancel")], limit=1)
            if mls:
                duplicated.append(imei)
                continue

            product = lot.product_id
            if not product:
                ignored.append(imei)
                continue

            # 4) Encontrar/crear el move del producto en este picking
            move = Move.search([("picking_id", "=", picking.id), ("product_id", "=", product.id)], limit=1)
            if not move:
                move = Move.create({
                    "name": product.display_name or product.name,
                    "product_id": product.id,
                    "product_uom": product.uom_id.id,
                    "product_uom_qty": 0.0,  # trabajaremos con move lines directas
                    "picking_id": picking.id,
                    "location_id": loc_src.id,
                    "location_dest_id": picking.location_dest_id.id,
                })

            # 5) Crear la línea del movimiento con qty_done=1 y el lote existente
            MoveLine.create({
                "picking_id": picking.id,
                "move_id": move.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "qty_done": 1.0,
                "location_id": loc_src.id,
                "location_dest_id": picking.location_dest_id.id,
                "lot_id": lot.id,  # usamos lote EXISTENTE (no lot_name)
            })
            processed.append(imei)

        # Armar resumen
        log = []
        if processed:
            log.append(_("✅ Añadidos: %s") % ", ".join(processed))
        if not_found:
            log.append(_("❌ No existen en Odoo: %s") % ", ".join(not_found))
        if not_in_wh:
            log.append(_("⚠️ Sin stock en WH/Stock: %s") % ", ".join(not_in_wh))
        if duplicated:
            log.append(_("⚠️ Ya usados en otro picking: %s") % ", ".join(duplicated))
        if ignored:
            log.append(_("ℹ️ Ignorados (sin producto): %s") % ", ".join(ignored))

        self.result_log = "\n".join(log) if log else _("No se procesó ningún número.")

        # Devolver el wizard con el resultado
        return {
            "type": "ir.actions.act_window",
            "res_model": "cf.serial.import.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "name": _("Importar números de serie"),
        }