
from odoo import models, fields, api, _
from datetime import timedelta

class CfProductivityReport(models.Model):
    # Campo técnico para decoraciones (no visible)
    time_since_previous_secs = fields.Integer(string='Segundos desde anterior', compute='_compute_time_since_previous_secs', store=False)

    # Campos opcionales para visualización
    validations_today = fields.Integer(string='Validaciones hoy', compute='_compute_validations_today', store=False)
    rank_today = fields.Integer(string='Ranking Diario', compute='_compute_rank_today', store=False)

    @api.depends('time_since_previous')
    def _compute_time_since_previous_secs(self):
        for rec in self:
            secs = 0
            val = rec.time_since_previous or ''
            try:
                parts = [int(p) for p in val.split(':')]
                while len(parts) < 3:
                    parts.insert(0, 0)
                h, m, s = parts[-3], parts[-2], parts[-1]
                secs = h*3600 + m*60 + s
            except Exception:
                secs = 0
            rec.time_since_previous_secs = secs

    def _compute_validations_today(self):
        # Valor por defecto seguro (0) si no hay lógica específica
        for rec in self:
            rec.validations_today = 0

    def _compute_rank_today(self):
        # Valor por defecto seguro (0); puede ser recalculado por acción manual externa
        for rec in self:
            rec.rank_today = 0

    _name = "cf.productivity.report"
    _description = "Informe de Productividad"
    _order = "date desc, id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Descripción", compute="_compute_name", store=False)
    date = fields.Datetime(string="Fecha", required=True, default=fields.Datetime.now, index=True)
    user_id = fields.Many2one('res.users', string="Usuario", required=True, index=True, default=lambda self: self.env.user)
    action_type = fields.Selection([
        ('order', 'Pedido/Entrega validada'),
        ('repair', 'Reparación'),
        ('ticket', 'Helpdesk/Ticket'),
        ('other', 'Otro'),
    ], string="Tipo de acción", default='order', index=True)
    model = fields.Char(string="Modelo origen")
    res_id = fields.Integer(string="ID origen")
    reason = fields.Char(string="Motivo")
    note = fields.Text(string="Nota interna")

    # KPIs
    time_since_previous = fields.Char(string="🕒 Tiempo desde anterior", compute="_compute_time_since_previous", store=False)
    is_pause = fields.Boolean(string="Pausa detectada", compute="_compute_is_pause", store=False)
    pause_threshold_min = fields.Integer(string="Umbral pausa (min)", default=30, help="Si el tiempo desde anterior supera este valor, se marca como pausa.")

    avg_time_today = fields.Char(string="Tiempo medio de hoy", compute="_compute_avg_time_today", store=False)

    @api.depends('date', 'user_id', 'action_type', 'reason')
    def _compute_name(self):
        for rec in self:
            bits = [rec.date and rec.date.strftime('%Y-%m-%d %H:%M:%S') or '', rec.user_id.name or '', rec.action_type or '']
            if rec.reason:
                bits.append(rec.reason)
            rec.name = " | ".join([b for b in bits if b])

    @api.depends('user_id', 'date')
    def _compute_time_since_previous(self):
        for record in self:
            record.time_since_previous = ''
            if not record.user_id or not record.date:
                continue
            previous = self.search([
                ('id', '!=', record.id),
                ('user_id', '=', record.user_id.id),
                ('date', '<', record.date),
            ], order='date desc, id desc', limit=1)
            if previous:
                delta = record.date - previous.date
                total_seconds = int(delta.total_seconds())
                hh = total_seconds // 3600
                mm = (total_seconds % 3600) // 60
                ss = total_seconds % 60
                record.time_since_previous = f"{hh:02d}:{mm:02d}:{ss:02d}"

    @api.depends('time_since_previous', 'pause_threshold_min')
    def _compute_is_pause(self):
        for rec in self:
            rec.is_pause = False
            if rec.time_since_previous:
                try:
                    hh, mm, ss = rec.time_since_previous.split(':')
                    total = int(hh) * 3600 + int(mm) * 60 + int(ss)
                    rec.is_pause = total >= rec.pause_threshold_min * 60
                except Exception:
                    rec.is_pause = False

    def _compute_avg_time_today(self):
        for rec in self:
            rec.avg_time_today = ''
            if not rec.user_id or not rec.date:
                continue
            start = fields.Datetime.to_string(fields.Datetime.context_timestamp(rec, rec.date).replace(hour=0, minute=0, second=0, microsecond=0))
            end = fields.Datetime.to_string(fields.Datetime.context_timestamp(rec, rec.date).replace(hour=23, minute=59, second=59, microsecond=999999))
            lines = self.search([('user_id', '=', rec.user_id.id), ('date', '>=', start), ('date', '<=', end)], order='date asc')
            prev_date = None
            gaps = []
            for l in lines:
                if prev_date:
                    gaps.append((l.date - prev_date).total_seconds())
                prev_date = l.date
            if gaps:
                avg = sum(gaps) / len(gaps)
                hh = int(avg) // 3600
                mm = (int(avg) % 3600) // 60
                ss = int(avg) % 60
                rec.avg_time_today = f"{hh:02d}:{mm:02d}:{ss:02d}"
            else:
                rec.avg_time_today = ''

    # Helpers to create log lines from other models (optional public methods)
    @api.model
    def log_action(self, action_type='order', model=None, res_id=None, reason=None, user_id=None, date=None):
        vals = {
            'action_type': action_type,
            'model': model,
            'res_id': res_id or 0,
            'reason': reason or False,
            'user_id': user_id or self.env.uid,
            'date': date or fields.Datetime.now(),
        }
        return self.create(vals)

time_since_previous_sec = fields.Integer(string="Segundos desde anterior", compute="_compute_time_since_previous_sec", store=False)

def _compute_time_since_previous_sec(self):
    for rec in self:
        rec.time_since_previous_sec = 0
        if rec.time_since_previous:
            try:
                hh, mm, ss = rec.time_since_previous.split(":")
                rec.time_since_previous_sec = int(hh) * 3600 + int(mm) * 60 + int(ss)
            except Exception:
                rec.time_since_previous_sec = 0

