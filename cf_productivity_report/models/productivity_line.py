# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CFProductivityLine(models.Model):
    _name = "cf.productivity.line"
    _description = "CF Productividad - Registro"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Datetime("Fecha", default=lambda self: fields.Datetime.now(), index=True)
    user_id = fields.Many2one("res.users", "Usuario", required=True, index=True)
    type = fields.Selection([
        ("repair", "Reparación"),
        ("ticket", "Ticket respondido"),
        ("order",  "Pedido/Entrega validada"),
    ], string="Tipo", required=True, index=True)
    reason = fields.Char("Motivo")
    ref_model = fields.Char("Modelo de referencia")
    ref_id = fields.Integer("ID referencia")

    def name_get(self):
        res = []
        for r in self:
            name = f"{r.user_id.name or '-'} - {dict(self._fields['type'].selection).get(r.type)}"
            res.append((r.id, name))
        return res

    @api.model
    def log_entry(self, *, user=None, type_key=None, reason=None, ref_model=None, ref_id=None):
        user = user or self.env.user
        if not type_key:
            return False
        return self.create({
            "user_id": user.id,
            "type": type_key,
            "reason": reason or False,
            "ref_model": ref_model or False,
            "ref_id": ref_id or False,
        })

from odoo import SUPERUSER_ID
import threading, logging
_logger = logging.getLogger(__name__)

class CFProductivityLine(models.Model):
    _inherit = "cf.productivity.line"

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        def _delayed_update():
            try:
                # Reabrir entorno seguro para hilo ajeno
                with api.Environment.manage():
                    with self.env.registry.cursor() as cr:
                        env2 = api.Environment(cr, SUPERUSER_ID, {})
                        env2["cf.productivity.summary"].sudo().action_update_productivity_summary()
            except Exception as e:
                _logger.exception("Productivity summary update failed: %s", e)
        threading.Timer(10.0, _delayed_update).start()
        return rec
