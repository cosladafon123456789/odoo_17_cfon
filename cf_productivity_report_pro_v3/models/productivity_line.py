
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
import html

class CFProductivityLine(models.Model):
    _name = "cf.productivity.line"
    _description = "CF Productividad - Registro"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Datetime("Fecha", default=lambda self: fields.Datetime.now(), index=True)
    user_id = fields.Many2one("res.users", "Usuario", required=True, index=True)
    type = fields.Selection([
        ("repair", "Reparación"),
        ("ticket", "Ticket/Helpdesk"),
        ("order",  "Pedido/Entrega validada"),
    ], string="Tipo", required=True, index=True)
    reason = fields.Char("Motivo")
    ref_model = fields.Char("Modelo de referencia")
    ref_id = fields.Integer("ID referencia")
    duration_seconds = fields.Integer("Duración (segundos)", default=0, help="Tiempo dedicado estimado/real a la tarea")
    points = fields.Float("Puntos", compute="_compute_points", store=True)

    @api.depends("type")
    def _compute_points(self):
        for r in self:
            r.points = {"repair": 2.0, "order": 1.5, "ticket": 1.0}.get(r.type, 1.0)

    def name_get(self):
        res = []
        for r in self:
            name = f"{r.user_id.name or '-'} - {dict(self._fields['type'].selection).get(r.type)}"
            if r.reason:
                name += f" ({r.reason})"
            res.append((r.id, name))
        return res

    @api.model
    def log_entry(self, *, user=None, type_key=None, reason=None, ref_model=None, ref_id=None, duration_seconds=0):
        user = user or self.env.user
        if not type_key:
            return False
        return self.create({
            "user_id": user.id,
            "type": type_key,
            "reason": reason or False,
            "ref_model": ref_model or False,
            "ref_id": ref_id or False,
            "duration_seconds": duration_seconds or 0,
        })

    @api.model
    def _block_metrics_for_day(self, target_date=None, user=None, inactivity_minutes=None):
        if not target_date:
            target_date = fields.Date.context_today(self)
        start = fields.Datetime.to_datetime(f"{target_date} 00:00:00")
        end = fields.Datetime.to_datetime(f"{target_date} 23:59:59")

        if inactivity_minutes is None:
            inactivity_minutes = self.env.company.cf_inactivity_minutes or 30
        inactivity_minutes = max(5, inactivity_minutes)

        domain_base = [('date', '>=', start), ('date', '<=', end)]
        users = self.env['res.users'].browse([user.id]) if user else self.env['res.users'].search([])
        res = {}

        for u in users:
            lines = self.search(domain_base + [('user_id','=', u.id)], order='date asc')
            if not lines:
                continue
            block_start = lines[0].date
            last = lines[0].date
            actions = 1
            effective_minutes = 0.0
            for line in lines[1:]:
                diff = (line.date - last).total_seconds() / 60.0
                if diff > inactivity_minutes:
                    effective_minutes += (last - block_start).total_seconds() / 60.0
                    block_start = line.date
                last = line.date
                actions += 1
            effective_minutes += (last - block_start).total_seconds() / 60.0
            avg = (effective_minutes / actions) if actions else 0.0
            res[u.id] = {
                'user': u,
                'actions': actions,
                'effective_minutes': round(effective_minutes, 2),
                'avg_minutes': round(avg, 2),
            }
        return res

    @api.model
    def _order_intervals_for_day(self, target_date=None, user=None, reset_minutes=None):
        if not target_date:
            target_date = fields.Date.context_today(self)
        start = fields.Datetime.to_datetime(f"{target_date} 00:00:00")
        end = fields.Datetime.to_datetime(f"{target_date} 23:59:59")

        if reset_minutes is None:
            reset_minutes = self.env.company.cf_order_reset_minutes or self.env.company.cf_inactivity_minutes or 30
        reset_minutes = max(5, reset_minutes)

        domain_base = [('date', '>=', start), ('date', '<=', end), ('type', '=', 'order')]
        users = self.env['res.users'].browse([user.id]) if user else self.env['res.users'].search([])
        res = {}

        for u in users:
            orders = self.search(domain_base + [('user_id','=', u.id)], order='date asc')
            if not orders or len(orders) < 2:
                res[u.id] = {'user': u, 'avg_between_orders': 0.0, 'blocks': 0, 'orders': len(orders)}
                continue

            blocks = 1
            intervals_minutes = []
            last = orders[0].date
            for line in orders[1:]:
                diff = (line.date - last).total_seconds() / 60.0
                if diff > reset_minutes:
                    blocks += 1
                else:
                    intervals_minutes.append(diff)
                last = line.date
            avg_between = sum(intervals_minutes)/len(intervals_minutes) if intervals_minutes else 0.0
            res[u.id] = {
                'user': u,
                'avg_between_orders': round(avg_between, 2),
                'blocks': blocks,
                'orders': len(orders),
            }
        return res

    @api.model
    def action_send_daily_report(self):
        today = fields.Date.context_today(self)

        kpi_blocks = self._block_metrics_for_day(today)
        kpi_orders = self._order_intervals_for_day(today)

        admins = self.env.ref('base.group_system').users
        access_group = self.env.ref('cf_productivity_report_pro_v3.group_cf_productivity_access', raise_if_not_found=False)
        access_users = access_group.users if access_group else self.env['res.users']
        recipients = (admins | access_users).filtered(lambda u: u.active and u.partner_id.email)
        if not recipients:
            return True

        def fmt_min(m):
            h = int(m // 60)
            mins = int(m % 60)
            return (f"{h}h {mins:02d}m" if h else f"{mins}m")

        rows = []
        total_actions, total_eff = 0, 0.0
        all_user_ids = set(list(kpi_blocks.keys()) + list(kpi_orders.keys()))
        for uid in sorted(all_user_ids):
            user = kpi_blocks.get(uid, {}).get('user') or kpi_orders.get(uid, {}).get('user')
            actions = kpi_blocks.get(uid, {}).get('actions', 0)
            eff_min = kpi_blocks.get(uid, {}).get('effective_minutes', 0.0)
            avg = kpi_blocks.get(uid, {}).get('avg_minutes', 0.0)
            avg_between_orders = kpi_orders.get(uid, {}).get('avg_between_orders', 0.0)

            total_actions += actions
            total_eff += eff_min
            rows.append(f"""<tr>
                <td>{html.escape(user.name if user else '')}</td>
                <td style='text-align:right'>{actions}</td>
                <td style='text-align:right'>{fmt_min(eff_min)}</td>
                <td style='text-align:right'>{avg:.2f} min</td>
                <td style='text-align:right'>{(str(avg_between_orders)+' min') if avg_between_orders else '-'}</td>
            </tr>""")
        rows_html = "".join(rows)
        global_avg = (total_eff / total_actions) if total_actions else 0.0

        company = self.env.company
        inact = company.cf_inactivity_minutes or 30
        reset = company.cf_order_reset_minutes or inact

        body_html = f"""
            <div style='font-family:Arial,Helvetica,sans-serif'>
                <h3>Resumen de Productividad — {today}</h3>
                <p><b>Empresa:</b> {html.escape(company.name or '')}</p>
                <p><b>Regla de inactividad (bloques):</b> {inact} min — <b>Reseteo pedidos:</b> {reset} min</p>
                <table border='1' cellspacing='0' cellpadding='6' style='border-collapse:collapse; width:100%;'>
                    <thead>
                        <tr style='background:#f2f2f2'>
                            <th>Usuario</th>
                            <th style='text-align:right'>Acciones</th>
                            <th style='text-align:right'>Tiempo efectivo</th>
                            <th style='text-align:right'>Media (min/acción)</th>
                            <th style='text-align:right'>Media entre pedidos</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                    <tfoot>
                        <tr style='background:#fafafa'>
                            <td><b>Total</b></td>
                            <td style='text-align:right'><b>{total_actions}</b></td>
                            <td style='text-align:right'><b>{fmt_min(total_eff)}</b></td>
                            <td style='text-align:right'><b>{global_avg:.2f} min</b></td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
                <p style='color:#666;margin-top:10px'>Informe generado automáticamente a las 20:00.</p>
            </div>
        """

        Mail = self.env['mail.mail'].sudo()
        subject = f"Productividad diaria — {today} ({company.name})"
        for user in recipients:
            Mail.create({
                'subject': subject,
                'body_html': body_html,
                'email_to': user.partner_id.email,
                'auto_delete': True,
            }).send()
        return True
