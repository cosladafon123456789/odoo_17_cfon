from odoo import fields, models, _

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
        payload = {"thread_id": ticket.external_id, "message": self.message}
        files = None
        if self.attachment_ids:
            files = []
            for att in self.attachment_ids:
                data = att._file_read(att.store_fname, bin_size=False) if att.store_fname else None
                if isinstance(data, str):
                    data = data.encode("utf-8")
                files.append(("files", (att.name or "adjunto.bin", data or b"", att.mimetype or "application/octet-stream")))
        acc._api_post("/api/messages/reply", payload=payload, files=files)
        self.env["marketplace.message"].create({
            "ticket_id": ticket.id,
            "direction": "out",
            "author": self.env.user.name,
            "body": self.message,
        })
        ticket.status = "answered"
        return {"type":"ir.actions.act_window_close"}