from odoo import fields, models, _

class MarketplaceTicket(models.Model):
    _name = "marketplace.ticket"
    _description = "Ticket de Marketplace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Asunto", required=True, tracking=True)
    external_id = fields.Char(string="ID Externo", index=True, readonly=True)
    account_id = fields.Many2one("marketplace.account", required=True, tracking=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Cliente", tracking=True)
    order_reference = fields.Char(string="Referencia de pedido", tracking=True)
    status = fields.Selection([("open","Abierto"),("answered","Respondido"),("pending","Pendiente"),("closed","Cerrado")], default="open", tracking=True)
    message_ids = fields.One2many("marketplace.message","ticket_id", string="Mensajes")
    message_count = fields.Integer(compute="_compute_message_count")

    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)