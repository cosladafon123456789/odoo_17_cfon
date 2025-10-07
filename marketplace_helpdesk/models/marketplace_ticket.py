from odoo import api, fields, models

class MarketplaceTicket(models.Model):
    _name = "marketplace.ticket"
    _description = "Ticket de Marketplace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "last_message_date desc, create_date desc"

    name = fields.Char(string="Asunto", required=True, tracking=True)
    account_id = fields.Many2one("marketplace.account", string="Cuenta", ondelete="set null", tracking=True)
    marketplace = fields.Char(string="Marketplace", tracking=True)
    external_id = fields.Char(string="ID externo", index=True, readonly=True)
    customer_name = fields.Char(string="Nombre cliente", tracking=True)
    customer_email = fields.Char(string="Email cliente")
    state = fields.Selection([
        ("new", "Nuevo"),
        ("in_progress", "En proceso"),
        ("answered", "Respondido"),
        ("closed", "Cerrado"),
    ], string="Estado", default="new", tracking=True)

    last_external_update = fields.Datetime(string="Última actualización externa", readonly=True)
    participants = fields.Char(string="Participantes (texto)")
    message_count = fields.Integer(string="Recuento de mensajes", compute="_compute_message_count", store=False)
    last_message_date = fields.Datetime(string="Fecha último mensaje", compute="_compute_last_message_date", store=False)

    @api.depends("message_ids")
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)

    @api.depends("message_ids")
    def _compute_last_message_date(self):
        for rec in self:
            rec.last_message_date = max(rec.message_ids.mapped("date")) if rec.message_ids else rec.create_date

    def action_mark_in_progress(self):
        self.write({"state": "in_progress"})

    def action_mark_closed(self):
        self.write({"state": "closed"})

    def action_sync_messages(self):
        return True
