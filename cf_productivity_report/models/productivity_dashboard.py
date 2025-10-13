# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, time

class CFProductivityDashboard(models.TransientModel):
    _name = "cf.productivity.dashboard"
    _description = "Resumen de Productividad"
    _transient_max_hours = 0  # keep until session ends

    # KPIs
    validations_today = fields.Integer("Validaciones hoy")
    avg_interval_hhmmss = fields.Char("Media entre validaciones (hh:mm:ss)")
    last_validation = fields.Datetime("Última validación")
    tickets_today = fields.Integer("Tickets gestionados hoy")
    repairs_today = fields.Integer("Reparaciones finalizadas hoy")

    def _get_domain_today(self, type_key=None, only_me=False):
        user_id = self.env.user.id if only_me else False
        today = fields.Date.context_today(self)
        start = fields.Datetime.to_datetime(f"{today} 00:00:00")
        end = fields.Datetime.to_datetime(f"{today} 23:59:59")
        dom = [('date', '>=', start), ('date', '<=', end)]
        if type_key:
            if isinstance(type_key, (list, tuple)):
                dom.append(('type', 'in', list(type_key)))
            else:
                dom.append(('type', '=', type_key))
        if only_me:
            dom.append(('user_id', '=', user_id))
        return dom

    @api.model
    def open_dashboard(self):
        # Create/refresh one record each time
        only_me = bool(self.env.context.get('only_me'))
        Line = self.env['cf.productivity.line'].sudo()

        dom_orders = self._get_domain_today('order', only_me)
        validations_today = Line.search_count(dom_orders)

        # Average interval (sec) where interval exists
        intervals = Line.read_group(
            dom_orders + [('interval_seconds', '!=', False)],
            ['interval_seconds:avg'],
            []
        )
        avg_sec = int(intervals[0]['interval_seconds_avg']) if intervals and intervals[0].get('interval_seconds_avg') else 0
        h = avg_sec // 3600
        m = (avg_sec % 3600) // 60
        s = avg_sec % 60
        avg_hms = f"{h:02d}:{m:02d}:{s:02d}"

        last = Line.search(dom_orders, limit=1, order='date desc, id desc').date

        tickets_today = Line.search_count(self._get_domain_today(['ticket', 'ticket_stage'], only_me))
        repairs_today = Line.search_count(self._get_domain_today('repair', only_me))

        rec = self.create({
            'validations_today': validations_today,
            'avg_interval_hhmmss': avg_hms,
            'last_validation': last,
            'tickets_today': tickets_today,
            'repairs_today': repairs_today,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Resumen de Productividad',
            'res_model': 'cf.productivity.dashboard',
            'view_mode': 'form',
            'res_id': rec.id,
            'target': 'current',
        }
