from odoo import api, fields, models, _

class EmployeeProductivityLog(models.Model):
    _name = "employee.productivity.log"
    _description = "Employee Productivity Log"
    _order = "date desc, id desc"

    date = fields.Datetime(string="Fecha", default=lambda self: fields.Datetime.now(), index=True)
    user_id = fields.Many2one("res.users", string="Empleado", required=True, index=True)
    action_type = fields.Selection([
        ("picking", "Pedido"),
        ("repair", "Reparación"),
        ("ticket", "Ticket")
    ], string="Tipo de acción", required=True, index=True)

    related_model = fields.Char(string="Modelo relacionado")
    related_id = fields.Integer(string="ID relacionado")

    picking_id = fields.Many2one("stock.picking", string="Entrega", compute="_compute_relations", store=False)
    repair_id = fields.Many2one("repair.order", string="Reparación", compute="_compute_relations", store=False)
    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket", compute="_compute_relations", store=False)

    repair_reason_id = fields.Many2one("cf.repair.reason", string="Motivo de reparación")

    @api.depends("related_model", "related_id")
    def _compute_relations(self):
        for rec in self:
            rec.picking_id = False
            rec.repair_id = False
            rec.ticket_id = False
            if rec.related_model == "stock.picking" and rec.related_id:
                rec.picking_id = self.env["stock.picking"].browse(rec.related_id)
            elif rec.related_model == "repair.order" and rec.related_id:
                rec.repair_id = self.env["repair.order"].browse(rec.related_id)
            elif rec.related_model == "helpdesk.ticket" and rec.related_id:
                rec.ticket_id = self.env["helpdesk.ticket"].browse(rec.related_id)
