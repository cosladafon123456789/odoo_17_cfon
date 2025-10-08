
from odoo import fields, models

class MarketplaceMessage(models.Model):
    _name = "marketplace.message"
    _description = "Mensaje de Ticket Marketplace"
    ticket_id = fields.Many2one("marketplace.ticket", required=True)
    external_id = fields.Char()
    author = fields.Char()
    body = fields.Text()
    direction = fields.Selection([("in","Entrante"),("out","Saliente")], default="in")
