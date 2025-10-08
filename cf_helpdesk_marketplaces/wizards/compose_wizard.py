
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MarketplaceComposeWizard(models.TransientModel):
    _name = "marketplace.compose.wizard"
    _description = "Responder a ticket de marketplace"

    ticket_id = fields.Many2one("marketplace.ticket", required=True)
    message = fields.Text(required=True, string="Mensaje")
    attachment_ids = fields.Many2many("ir.attachment", string="Adjuntos")

    def action_send(self):
        self.ensure_one()
        ticket = self.ticket_id
        acc = ticket.account_id
        # Example Mirakl reply endpoint; adjust to the real one.
        # Payload will vary by marketplace; adapt here.
        payload = {
            "thread_id": ticket.external_id,
            "message": self.message,
        }
        files = []
        for att in self.attachment_ids:
            files.append(("files", (att.name, att._file_read(att.store_fname, bin_size=False), att.mimetype)))
        res = acc._api_post("/api/messages/reply", payload=payload, files=files if files else None)
        # Log locally
        self.env["marketplace.message"].create({
            "ticket_id": ticket.id,
            "direction": "out",
            "author": self.env.user.name,
            "body": self.message,
        })
        ticket.status = "answered"
        return {"type":"ir.actions.act_window_close"}
