from odoo import api, fields, models
from datetime import timedelta

class CfAnalisisDevolucionesProPlus(models.TransientModel):
    _name = "cf.analisis.devoluciones.pro.plus"
    _description = "Análisis de Devoluciones PRO+"

    fecha_desde = fields.Date(string="Desde")
    fecha_hasta = fields.Date(string="Hasta")
    total_devoluciones = fields.Integer(string="📦 Total devoluciones", compute="_compute_kpis")
    total_ventas = fields.Integer(string="Pedidos en periodo", compute="_compute_kpis")
    pct_sobre_ventas = fields.Float(string="💰 % sobre ventas", compute="_compute_kpis", digits=(16,2))
    internos = fields.Integer(string="⚙️ Internos", compute="_compute_kpis")
    externos = fields.Integer(string="🔁 Externos", compute="_compute_kpis")
    media_dias = fields.Float(string="⏱️ Días medios", compute="_compute_kpis", digits=(16,2))

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
            if rec.fecha_desde:
                domain_dev.append(('fecha_devolucion','>=',fields.Datetime.to_datetime(rec.fecha_desde)))
            if rec.fecha_hasta:
                domain_dev.append(('fecha_devolucion','<',fields.Datetime.to_datetime(rec.fecha_hasta) + timedelta(days=1)))
            devoluciones = Sale.search(domain_dev)
            ventas_domain = []
            if rec.fecha_desde:
                ventas_domain.append(('date_order','>=',fields.Datetime.to_datetime(rec.fecha_desde)))
            if rec.fecha_hasta:
                ventas_domain.append(('date_order','<',fields.Datetime.to_datetime(rec.fecha_hasta) + timedelta(days=1)))
            ventas = Sale.search(ventas_domain)
            rec.total_devoluciones = len(devoluciones)
            rec.total_ventas = len(ventas)
            rec.pct_sobre_ventas = (rec.total_devoluciones / rec.total_ventas * 100.0) if rec.total_ventas else 0.0
            if has_tipo and has_motivo:
                rec.internos = Sale.search_count(domain_dev + [('tipo_error_devolucion','=','interno')])
                rec.externos = Sale.search_count(domain_dev + [('tipo_error_devolucion','=','externo')])
            else:
                rec.internos = 0
                rec.externos = 0
            total_days = 0.0
            count = 0
            for o in devoluciones:
                if o.fecha_devolucion and o.date_order:
                    delta = fields.Datetime.from_string(o.fecha_devolucion) - fields.Datetime.from_string(o.date_order)
                    total_days += delta.total_seconds() / 86400.0
                    count += 1
            rec.media_dias = (total_days / count) if count else 0.0

    def action_open_graph_motivos(self):
        self.ensure_one()
        return {'type':'ir.actions.act_window','name':'Motivos de devolución','res_model':'sale.order','view_mode':'graph','domain':[('motivo_devolucion','!=',False)],'context':{'graph_measure':'__count','graph_mode':'bar','group_by':['motivo_devolucion']}}

    def action_open_graph_tipo_error(self):
        self.ensure_one()
        return {'type':'ir.actions.act_window','name':'Distribución por tipo de error','res_model':'sale.order','view_mode':'graph','context':{'graph_measure':'__count','graph_mode':'pie','group_by':['tipo_error_devolucion']}}

    def action_open_graph_mes(self):
        self.ensure_one()
        return {'type':'ir.actions.act_window','name':'Evolución mensual','res_model':'sale.order','view_mode':'graph','context':{'graph_measure':'__count','graph_mode':'line','group_by':['fecha_devolucion:month']}}

    def action_open_pivot(self):
        self.ensure_one()
        IrField = self.env['ir.model.fields'].sudo()
        has_motivo = IrField.search_count([('model','=','sale.order'),('name','=','motivo_devolucion')]) > 0
        has_tipo = IrField.search_count([('model','=','sale.order'),('name','=','tipo_error_devolucion')]) > 0
        ctx = {'pivot_measures':['__count']}
        domain = []
        if has_motivo and has_tipo:
            ctx['group_by'] = ['motivo_devolucion','tipo_error_devolucion']
            domain = [('motivo_devolucion','!=',False)]
        elif has_motivo:
            ctx['group_by'] = ['motivo_devolucion']
            domain = [('motivo_devolucion','!=',False)]
        return {'type':'ir.actions.act_window','name':'Pivot de devoluciones','res_model':'sale.order','view_mode':'pivot','domain':domain,'context':ctx}
