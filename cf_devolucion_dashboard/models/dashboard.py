from odoo import api, fields, models

class CfDevolucionDashboard(models.TransientModel):
    _name = "cf.devolucion.dashboard"
    _description = "Dashboard de devoluciones (KPIs)"

    total_devoluciones = fields.Integer(string="Total devoluciones", compute="_compute_kpis")
    total_ventas = fields.Integer(string="Total ventas", compute="_compute_kpis")
    pct_sobre_ventas = fields.Float(string="% sobre ventas", compute="_compute_kpis", digits=(16,2))
    internos = fields.Integer(string="Errores internos", compute="_compute_kpis")
    externos = fields.Integer(string="Errores externos", compute="_compute_kpis")
    media_dias = fields.Float(string="Días medios hasta devolución", compute="_compute_kpis", digits=(16,2))

    fecha_desde = fields.Date(string="Desde")
    fecha_hasta = fields.Date(string="Hasta")

    @api.depends('fecha_desde','fecha_hasta')
    def _compute_kpis(self):
        Sale = self.env['sale.order']
        for rec in self:
            domain_dev = [('motivo_devolucion','!=',False)]
            domain_all = []
            # Filtros de fecha
            if rec.fecha_desde:
                domain_dev.append(('fecha_devolucion','>=',fields.Datetime.to_datetime(rec.fecha_desde)))
                domain_all.append(('date_order','>=',fields.Datetime.to_datetime(rec.fecha_desde)))
            if rec.fecha_hasta:
                domain_dev.append(('fecha_devolucion','<=',fields.Datetime.to_datetime(rec.fecha_hasta) + fields.DateUtils.relativedelta(days=1)))
                domain_all.append(('date_order','<=',fields.Datetime.to_datetime(rec.fecha_hasta) + fields.DateUtils.relativedelta(days=1)))
            devoluciones = Sale.search(domain_dev)
            ventas = Sale.search(domain_all) if (rec.fecha_desde or rec.fecha_hasta) else Sale.search([])
            rec.total_devoluciones = len(devoluciones)
            rec.total_ventas = len(ventas) if ventas else 0
            rec.pct_sobre_ventas = (rec.total_devoluciones / rec.total_ventas * 100.0) if rec.total_ventas else 0.0
            rec.internos = Sale.search_count(domain_dev + [('tipo_error_devolucion','=','interno')])
            rec.externos = Sale.search_count(domain_dev + [('tipo_error_devolucion','=','externo')])
            # Media de días
            total_days = 0.0
            count = 0
            for o in devoluciones:
                if o.fecha_devolucion and o.date_order:
                    delta = fields.Datetime.from_string(o.fecha_devolucion) - fields.Datetime.from_string(o.date_order)
                    total_days += (delta.total_seconds() / 86400.0)
                    count += 1
            rec.media_dias = (total_days / count) if count else 0.0