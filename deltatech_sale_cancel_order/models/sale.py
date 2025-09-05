# ©  2023-now Terrabit
# See README.rst file on addons root folder for license details


from odoo import SUPERUSER_ID, _, fields, models
from odoo.tools.safe_eval import safe_eval


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cancel_requested = fields.Boolean("Cancel requested", default=False)

    def set_to_cancel(self, reason):
        self.ensure_one()
        # self.sudo().message_post(body=_("Cancellation requested by user. Reason: %s") % reason)
        self.sudo().write({"cancel_requested": True})
        if self.picking_ids:
            for picking in self.picking_ids:
                picking.sudo().message_post(body=_("Cancellation requested by user. Reason: %s") % reason)
                picking.sudo().write({"cancel_requested": True})

        # get partners to send the e-mail
        get_param = self.env["ir.config_parameter"].sudo().get_param
        if safe_eval(get_param("sale_cancel_order.default_email_send", "False")):
            try:
                partner_ids_to_send = safe_eval(get_param("sale_cancel_order.default_email_to", "False"))
            except Exception:
                partner_ids_to_send = False
            if partner_ids_to_send:
                if self.user_id and self.user_id.partner_id.id not in partner_ids_to_send:
                    partner_ids_to_send.append(self.user_id.partner_id.id)
            else:
                partner_ids_to_send = [self.user_id.partner_id.id]

            # send e-mail
            if partner_ids_to_send:
                email_values = {"recipient_ids": partner_ids_to_send}
                mail_template = self.env.ref("deltatech_sale_cancel_order.mail_template_cancel_order")
                mail_template.sudo().with_user(SUPERUSER_ID).send_mail(self.id, email_values=email_values)

    def write(self, vals):
        if "cancel_requested" in vals:
            picking_ids = self.mapped("picking_ids")
            picking_ids.sudo().write({"cancel_requested": vals["cancel_requested"]})

        return super().write(vals)
