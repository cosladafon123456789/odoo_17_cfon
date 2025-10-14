# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import SUPERUSER_ID

class CFProductivitySummary(models.Model):
    _name = "cf.productivity.summary"
    _description = "CF Productividad - Resumen Global"
    _order = "is_total desc, user_id asc"

    user_id = fields.Many2one("res.users", string="Usuario", index=True)
    repairs_done = fields.Integer(string="Reparaciones", default=0)
    tickets_done = fields.Integer(string="Tickets", default=0)
    orders_done  = fields.Integer(string="Entregas/Pedidos", default=0)
    total_done   = fields.Integer(string="Total", compute="_compute_total", store=False)
    avg_gap_minutes = fields.Float(string="Tiempo medio entre tareas (min)", default=0.0)
    is_total = fields.Boolean(string="Total general", default=False, index=True)
    last_update = fields.Datetime(string="Última actualización")

    @api.depends("repairs_done", "tickets_done", "orders_done")
    def _compute_total(self):
        for rec in self:
            rec.total_done = (rec.repairs_done or 0) + (rec.tickets_done or 0) + (rec.orders_done or 0)

    @api.model
    def action_update_productivity_summary(self):
        """Recalcula el resumen global por usuario y el total.
        - Cuenta por tipo (repair/ticket/order) a partir de cf.productivity.line
        - Calcula el tiempo medio entre validaciones sucesivas por usuario (todas las líneas)
        - Crea un registro TOTAL con la suma y la media global
        """
        Line = self.env["cf.productivity.line"].sudo()
        Summary = self.env["cf.productivity.summary"].sudo()

        # Borrar resúmenes anteriores
        Summary.search([]).unlink()

        # Obtener usuarios con líneas
        user_groups = Line.read_group(
            domain=[],
            fields=["user_id"],
            groupby=["user_id"],
            lazy=False,
        )
        all_gaps = []  # para media global
        created_recs = self.browse()

        for grp in user_groups:
            user_id = grp.get("user_id") and grp["user_id"][0]
            if not user_id:
                continue

            # Contadores por tipo
            cnt_repair = Line.search_count([("user_id", "=", user_id), ("type", "=", "repair")])
            cnt_ticket = Line.search_count([("user_id", "=", user_id), ("type", "=", "ticket")])
            cnt_order  = Line.search_count([("user_id", "=", user_id), ("type", "=", "order")])

            # Calcular gaps entre validaciones sucesivas (todas las líneas del usuario)
            lines = Line.search([("user_id", "=", user_id)], order="date asc, id asc")
            gaps = []
            last_dt = None
            for l in lines:
                if l.date:
                    if last_dt is not None:
                        delta = fields.Datetime.from_string(l.date) - fields.Datetime.from_string(last_dt)
                        minutes = delta.total_seconds() / 60.0
                        if minutes >= 0:
                            gaps.append(minutes)
                            all_gaps.append(minutes)
                    last_dt = l.date
            avg_gap = sum(gaps)/len(gaps) if gaps else 0.0

            created_recs |= Summary.create({
                "user_id": user_id,
                "repairs_done": cnt_repair,
                "tickets_done": cnt_ticket,
                "orders_done": cnt_order,
                "avg_gap_minutes": round(avg_gap, 2),
                "is_total": False,
                "last_update": fields.Datetime.now(),
            })

        # Crear TOTAL
        total_repair = int(sum(created_recs.mapped("repairs_done"))) if created_recs else 0
        total_ticket = int(sum(created_recs.mapped("tickets_done"))) if created_recs else 0
        total_order  = int(sum(created_recs.mapped("orders_done"))) if created_recs else 0
        total_avg    = round(sum(all_gaps)/len(all_gaps), 2) if all_gaps else 0.0

        Summary.create({
            "user_id": False,
            "repairs_done": total_repair,
            "tickets_done": total_ticket,
            "orders_done": total_order,
            "avg_gap_minutes": total_avg,
            "is_total": True,
            "last_update": fields.Datetime.now(),
        })

        action = self.env.ref("cf_productivity_report.action_cf_productivity_summary").read()[0]
        return action
