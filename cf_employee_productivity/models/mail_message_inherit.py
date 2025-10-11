from odoo import api, fields, models
from .res_config_settings import PARAM_HELPDESK_USERS

class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        configured_ids = self.env["res.config.settings"]._get_configured_user_ids(PARAM_HELPDESK_USERS)
        for msg in messages:
            # Only helpdesk.ticket messages, authored by configured user, and public (not internal)
            if msg.model == "helpdesk.ticket" and msg.author_id and msg.author_id.user_id:
                uid = msg.author_id.user_id.id
                if uid in configured_ids:
                    # Heuristic: public reply if not internal and message_type is comment/email
                    is_public = not getattr(msg, "is_internal", False)
                    if is_public and msg.message_type in ("comment", "email"):
                        self.env["employee.productivity.log"].sudo().create({
                            "user_id": uid,
                            "action_type": "ticket",
                            "related_model": "helpdesk.ticket",
                            "related_id": msg.res_id,
                        })
        return messages
