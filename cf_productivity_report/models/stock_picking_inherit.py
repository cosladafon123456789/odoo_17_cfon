# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            try:
                if picking.picking_type_id.code == "outgoing":
                    company_user = self.env.company.cf_user_order_id or self.env.user
                    # calcular intervalo con la última validación del mismo usuario
                    last_line = self.env['cf.productivity.line'].sudo().search([
                        ('user_id', '=', company_user.id),
                        ('type', '=', 'order'),
                    ], limit=1, order='date desc, id desc')

                    now_dt = fields.Datetime.now()
                    interval_seconds = False
                    reset_minutes = self.env.company.productivity_reset_minutes or 120
                    reset_seconds = reset_minutes * 60

                    if last_line:
                        delta = fields.Datetime.from_string(now_dt) - fields.Datetime.from_string(last_line.date)
                        interval = int(delta.total_seconds())
                        # Si supera umbral, consideramos reseteo y no guardamos intervalo
                        if interval <= reset_seconds:
                            interval_seconds = interval
                        else:
                            interval_seconds = False  # nuevo bloque

                    self.env["cf.productivity.line"].sudo().log_entry(
                        user=company_user,
                        type_key="order",
                        reason="Entrega validada",
                        ref_model="stock.picking",
                        ref_id=picking.id,
                        interval_seconds=interval_seconds,
                    )
            except Exception:
                # No bloquear validación por conteo de productividad
                continue
        return res
