
from odoo import fields, models, _

class MarketplaceTicket(models.Model):
    _name = "marketplace.ticket"
    _description = "Ticket de Marketplace"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    external_id = fields.Char(index=True)
    account_id = fields.Many2one("marketplace.account", required=True)
    partner_id = fields.Many2one("res.partner", string="Cliente")
    marketplace_name = fields.Char(string="Marketplace", default="MediaMarkt")
    status = fields.Selection([("open","Abierto"),("answered","Respondido"),("closed","Cerrado")], default="open")
    message_ids = fields.One2many("marketplace.message","ticket_id")
