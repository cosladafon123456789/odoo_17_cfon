# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class CFProductivityTicketDaily(models.Model):
    _name = "cf.productivity.ticket.daily"
    _description = "Productividad diaria en tickets Helpdesk (mensajes al cliente + cambios de etapa)"
    _auto = False
    _rec_name = "user_id"
    _order = "date desc, user_id"

    user_id = fields.Many2one("res.users", string="Usuario", readonly=True)
    date = fields.Date(string="Fecha", readonly=True)
    msg_count = fields.Integer(string="Mensajes enviados al cliente", readonly=True)
    stage_changes = fields.Integer(string="Cambios de etapa (Helpdesk)", readonly=True)
    total_interactions = fields.Integer(string="Total interacciones", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'cf_productivity_ticket_daily')
        self._cr.execute("""
            CREATE OR REPLACE VIEW cf_productivity_ticket_daily AS
            WITH base AS (
                SELECT
                    user_id,
                    DATE(date) AS date,
                    type,
                    reason,
                    ref
                FROM cf_productivity_line
                WHERE type = 'ticket'
            )
            SELECT
                ROW_NUMBER() OVER (ORDER BY date DESC, user_id) AS id,
                user_id,
                date,
                SUM(
                    CASE WHEN (ref LIKE 'helpdesk.ticket,%' OR ref IS NULL)
                          AND (reason ILIKE '%%mens%%' OR reason ILIKE '%%coment%%' OR reason ILIKE '%%respu%%')
                    THEN 1 ELSE 0 END
                ) AS msg_count,
                SUM(
                    CASE WHEN (ref LIKE 'helpdesk.ticket,%' OR ref IS NULL)
                          AND (reason ILIKE '%%etapa%%' OR reason ILIKE '%%estado%%' OR reason ILIKE '%%stage%%')
                    THEN 1 ELSE 0 END
                ) AS stage_changes,
                SUM(
                    CASE WHEN (ref LIKE 'helpdesk.ticket,%%' OR ref IS NULL)
                    THEN 1 ELSE 0 END
                ) AS total_interactions
            FROM base
            GROUP BY user_id, date
        """)
