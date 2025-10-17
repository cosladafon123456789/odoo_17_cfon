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
    stage_changes = fields.Integer(string="Cambios de etapa", readonly=True)
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
                    subtype,
                    model,
                    message_type,
                    is_internal
                FROM cf_productivity_line
                WHERE type = 'ticket'
            )
            SELECT
                ROW_NUMBER() OVER (ORDER BY date DESC, user_id) AS id,
                user_id,
                date,
                SUM(CASE WHEN model = 'helpdesk.ticket' AND message_type = 'comment' AND (is_internal IS NULL OR is_internal = FALSE) THEN 1 ELSE 0 END) AS msg_count,
                SUM(CASE WHEN model = 'helpdesk.ticket' AND subtype = 'stage_change' THEN 1 ELSE 0 END) AS stage_changes,
                SUM(CASE WHEN model = 'helpdesk.ticket' AND ((message_type = 'comment' AND (is_internal IS NULL OR is_internal = FALSE)) OR subtype = 'stage_change') THEN 1 ELSE 0 END) AS total_interactions
            FROM base
            GROUP BY user_id, date
        """)
