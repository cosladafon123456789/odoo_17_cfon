from odoo import api, fields, models

class CfDevolucionDashboard(models.TransientModel):
    _name = "cf.devolucion.dashboard.safe"
    _description = "Dashboard de devoluciones (SAFE)"

    # Filtros
    fecha_desde = fields.Date(string="Desde")
    fecha_hasta = fields.Date(string="Hasta")

    # KPIs
    total_devoluciones = fields.Integer(string="Total devoluciones", compute="_compute_kpis")
    total_ventas = fields.Integer(string="Total ventas", compute="_compute_kpis")
    pct_sobre_ventas = fields.Float(string="% sobre ventas", compute="_compute_kpis", digits=(16,2))
    internos = fields.Integer(string="Errores internos", compute="_compute_kpis")
    externos = fields.Integer(string="Errores externos", compute="_compute_kpis")
    media_dias = fields.Float(string="Días medios hasta devolución", compute="_compute_kpis", digits=(16,2))

    # Helpers: existen campos?
    has_motivo = fields.Boolean(compute="_compute_flags")
    has_tipo_error = fields.Boolean(compute="_compute_flags")

    @api.depends()
    def _compute_flags(self):
        IrField = self.env['ir.model.fields'].sudo()
        has_m = IrField.search_count([('model','=','sale.order'),('name','=','motivo_devolucion')]) > 0
        has_t = IrField.search_count([('model','=','sale.order'),('name','=','tipo_error_devolucion')]) > 0
        for r in self:
            r.has_motivo = has_m
            r.has_tipo_error = has_t

    @api.depends('fecha_desde','fecha_hasta')
    def _compute_kpis(self):
        Sale = self.env['sale.order']
        IrField = self.env['ir.model.fields'].sudo()
        has_motivo = IrField.search_count([('model','=','sale.order'),('name','=','motivo_devolucion')]) > 0
        has_tipo = IrField.search_count([('model','=','sale.order'),('name','=','tipo_error_devolucion')]) > 0

        for rec in self:
            domain_dev = []
            if has_motivo:
                domain_dev.append(('motivo_devolucion','!=',False))
            # Fechas: usamos fecha_devolucion si está; si no, date_order
            if rec.fecha_desde:
                domain_dev.append(('fecha_devolucion','>=',fields.Datetime.to_datetime(rec.fecha_desde)))
            if rec.fecha_hasta:
                # incluir todo el día: sumamos 1 día y usamos <
                domain_dev.append(('fecha_devolucion','<',fields.Datetime.to_datetime(rec.fecha_hasta) + fields.Date.to_date('1970-01-02') - fields.Date.to_date('1970-01-01')))

            devoluciones = Sale.search(domain_dev) if domain_dev else Sale.search([])
            ventas_domain = []
            if rec.fecha_desde:
                ventas_domain.append(('date_order','>=',fields.Datetime.to_datetime(rec.fecha_desde)))
            if rec.fecha_hasta:
                ventas_domain.append(('date_order','<',fields.Datetime.to_datetime(rec.fecha_hasta) + fields.Date.to_date('1970-01-02') - fields.Date.to_date('1970-01-01')))
            ventas = Sale.search(ventas_domain) if (rec.fecha_desde or rec.fecha_hasta) else Sale.search([])

            rec.total_devoluciones = len(devoluciones)
            rec.total_ventas = len(ventas) if ventas else 0
            rec.pct_sobre_ventas = (rec.total_devoluciones / rec.total_ventas * 100.0) if rec.total_ventas else 0.0

            if has_tipo and has_motivo:
                rec.internos = Sale.search_count(domain_dev + [('tipo_error_devolucion','=','interno')])
                rec.externos = Sale.search_count(domain_dev + [('tipo_error_devolucion','=','externo')])
            else:
                rec.internos = 0
                rec.externos = 0

            # Media días (si hay fecha_devolucion y date_order)
            total_days = 0.0
            count = 0
            for o in devoluciones:
                if o.fecha_devolucion and o.date_order:
                    delta = fields.Datetime.from_string(o.fecha_devolucion) - fields.Datetime.from_string(o.date_order)
                    total_days += delta.total_seconds() / 86400.0
                    count += 1
            rec.media_dias = (total_days / count) if count else 0.0

    # Botones que devuelven acciones seguras segun campos existentes
    def action_open_graph_motivos(self):
        self.ensure_one()
        IrField = self.env['ir.model.fields'].sudo()
        has_motivo = IrField.search_count([('model','=','sale.order'),('name','=','motivo_devolucion')]) > 0
        ctx = {'graph_measure': '__count', 'graph_mode': 'bar'}
        if has_motivo:
            ctx['group_by'] = ['motivo_devolucion']
            domain = [('motivo_devolucion','!=',False)]
        else:
            domain = []
        return {
            'type': 'ir.actions.act_window',
            'name': 'Motivos de devolución',
            'res_model': 'sale.order',
            'view_mode': 'graph',
            'domain': domain,
            'context': ctx,
        }

    def action_open_graph_tipo_error(self):
        self.ensure_one()
        IrField = self.env['ir.model.fields'].sudo()
        has_tipo = IrField.search_count([('model','=','sale.order'),('name','=','tipo_error_devolucion')]) > 0
        ctx = {'graph_measure': '__count', 'graph_mode': 'pie'}
        if has_tipo:
            ctx['group_by'] = ['tipo_error_devolucion']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Distribución por tipo de error',
            'res_model': 'sale.order',
            'view_mode': 'graph',
            'domain': [],
            'context': ctx,
        }

    def action_open_graph_mes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Evolución mensual',
            'res_model': 'sale.order',
            'view_mode': 'graph',
            'domain': [],
            'context': {'graph_measure': '__count', 'graph_mode': 'line', 'group_by': ['fecha_devolucion:month']},
        }

    def action_open_pivot(self):
        self.ensure_one()
        IrField = self.env['ir.model.fields'].sudo()
        has_motivo = IrField.search_count([('model','=','sale.order'),('name','=','motivo_devolucion')]) > 0
        has_tipo = IrField.search_count([('model','=','sale.order'),('name','=','tipo_error_devolucion')]) > 0
        ctx = {'pivot_measures': ['__count']}
        if has_motivo and has_tipo:
            ctx['group_by'] = ['motivo_devolucion','tipo_error_devolucion']
            domain = [('motivo_devolucion','!=',False)]
        elif has_motivo:
            ctx['group_by'] = ['motivo_devolucion']
            domain = [('motivo_devolucion','!=',False)]
        else:
            domain = []
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pivot de devoluciones',
            'res_model': 'sale.order',
            'view_mode': 'pivot',
            'domain': domain,
            'context': ctx,
        }