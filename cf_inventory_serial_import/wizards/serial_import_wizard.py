# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CFSerialImportWizard(models.TransientModel):
    _name = "cf.serial.import.wizard"
    _description = "Importación de Números de Serie (IMEI) al Picking con validación en WH/Stock"

    picking_id = fields.Many2one(
        "stock.picking",
        string="Albarán",
        required=True,
        ondelete="cascade"
    )
    imei_text = fields.Text(
        string="IMEIs / Números de serie (uno por línea)",
        required=True
    )
    result_log = fields.Html(
        string="Resultado",
        readonly=True
    )

    # -------------------------------------------------------------------------
    # UTILIDADES
    # -------------------------------------------------------------------------

    def _get_wh_stock_location(self):
        """Obtiene la ubicación WH/Stock (o Stock si no existe el path completo)."""
        location = self.env['stock.location'].search(
            [('complete_name', '=', 'WH/Stock')], limit=1
        )
        if not location:
            location = self.env['stock.location'].search(
                [('name', '=', 'Stock')], limit=1
            )
        return location

    def _clean_lines(self, text):
        """Limpia el texto pegado (elimina duplicados, espacios y caracteres raros)."""
        vals = []
        for line in (text or "").splitlines():
            s = (line or "").strip()
            if not s:
                continue
            s = s.replace(" ", "")
            s = "".join(ch for ch in s if ch.isalnum())
            if s:
                vals.append(s)
        seen, out = set(), []
        for v in vals:
            if v not in seen:
                seen.add(v)
                out.append(v)
        return out

    # -------------------------------------------------------------------------
    # PROCESAMIENTO
    # -------------------------------------------------------------------------

    def action_process(self):
        """Procesa los IMEIs pegados o escaneados y crea las líneas válidas."""
        self.ensure_one()
        picking = self.picking_id

        if picking.state in ("done", "cancel"):
            raise UserError(_("No se puede importar en un albarán validado o cancelado."))

        loc_src = self._get_wh_stock_location()
        if not loc_src:
            raise UserError(_("No se encontró la ubicación 'WH/Stock'."))

        processed, not_found, not_in_wh, duplicated, ignored = [], [], [], [], []

        lines = self._clean_lines(self.imei_text)
        if not lines:
            raise UserError(_("No se han introducido números de serie válidos."))

        Quant = self.env["stock.quant"]
        Lot = self.env["stock.lot"]
        Move = self.env["stock.move"]
        MoveLine = self.env["stock.move.line"]

        for imei in lines:
            # 1️⃣ Verificar existencia del lote
            lot = Lot.search([("name", "=", imei)], limit=1)
            if not lot:
                not_found.append(imei)
                continue

            # 2️⃣ Verificar si el IMEI está disponible (no reservado en otro picking activo)
            mls = MoveLine.search([
                ("lot_id", "=", lot.id),
                ("picking_id", "!=", picking.id),
                ("state", "not in", ["cancel", "done"])
            ], limit=1)

            if mls:
                duplicated.append(imei)
                continue

            # 3️⃣ Comprobar si el IMEI tiene stock disponible en WH/Stock
            domain_quant = [
                ("lot_id", "=", lot.id),
                ("location_id", "=", loc_src.id),
            ]
            if picking.company_id:
                domain_quant.append(("company_id", "=", picking.company_id.id))

            quants = Quant.search(domain_quant)
            available = sum(max(q.quantity - q.reserved_quantity, 0.0) for q in quants)

            if available <= 0:
                not_in_wh.append(imei)
                continue

            # 4️⃣ Obtener producto
            product = lot.product_id
            if not product:
                ignored.append(imei)
                continue

            # 5️⃣ Crear o encontrar movimiento
            move = Move.search([
                ("picking_id", "=", picking.id),
                ("product_id", "=", product.id)
            ], limit=1)
            if not move:
                move = Move.create({
                    "name": product.display_name or product.name,
                    "product_id": product.id,
                    "product_uom": product.uom_id.id,
                    "product_uom_qty": 0.0,
                    "picking_id": picking.id,
                    "location_id": loc_src.id,
                    "location_dest_id": picking.location_dest_id.id,
                })

            # 6️⃣ Crear línea de movimiento
            MoveLine.create({
                "picking_id": picking.id,
                "move_id": move.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "qty_done": 1.0,
                "location_id": loc_src.id,
                "location_dest_id": picking.location_dest_id.id,
                "lot_id": lot.id,
            })

            processed.append(imei)

        # ---------------------------------------------------------------------
        # 📋 RESUMEN DEL PROCESO
        # ---------------------------------------------------------------------
        log_lines = []
        if processed:
            log_lines.append(f"<b style='color:green;'>✅ Añadidos:</b> {', '.join(processed)}")
        if not_found:
            log_lines.append(f"<b style='color:red;'>❌ No existen en Odoo:</b> {', '.join(not_found)}")
        if not_in_wh:
            log_lines.append(f"<b style='color:orange;'>⚠️ Sin stock en WH/Stock:</b> {', '.join(not_in_wh)}")
        if duplicated:
            log_lines.append(f"<b style='color:#d4a017;'>⚠️ Ya usados en otro picking activo:</b> {', '.join(duplicated)}")
        if ignored:
            log_lines.append(f"<b style='color:gray;'>ℹ️ Ignorados (sin producto asociado):</b> {', '.join(ignored)}")

        self.result_log = "<br/>".join(log_lines) if log_lines else _("No se procesó ningún número de serie.")

        # Recargar el wizard mostrando resultados
        return {
            "type": "ir.actions.act_window",
            "res_model": "cf.serial.import.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "name": _("Importar números de serie"),
        }
