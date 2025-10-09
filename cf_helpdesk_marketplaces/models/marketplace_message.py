from odoo import fields, models

class MarketplaceMessage(models.Model):
    _name = "marketplace.message"
    _description = "Mensaje de Ticket Marketplace"
    _order = "date asc"

    ticket_id = fields.Many2one("marketplace.ticket", required=True, ondelete="cascade")
    external_id = fields.Char(index=True)
    author = fields.Char()
    date = fields.Datetime(default=fields.Datetime.now)
    direction = fields.Selection([("in","Entrante"),("out","Saliente")], default="in")
    body = fields.Text()
    attachment_ids = fields.Many2many("ir.attachment", string="Adjuntos")