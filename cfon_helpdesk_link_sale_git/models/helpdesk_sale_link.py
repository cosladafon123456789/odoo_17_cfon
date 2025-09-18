from odoo import api, fields, models
import re

# Patrón genérico para capturar nombres de pedidos (SO) en el título
ORDER_NAME_RE = re.compile(r"[A-Z0-9_/-]{5,}")

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # Enlace normalizado a la venta
    sale_link_id = fields.Many2one(
        "sale.order",
        string="Pedido relacionado (auto)",
        index=True,
        ondelete="set null",
    )

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        tickets._sync_sale_link_id()
        return tickets

    def write(self, vals):
        res = super().write(vals)
        # Re-sincronizamos cuando cambie el título u otros campos
        if {"name"} & set(vals.keys()) or True:
            self._sync_sale_link_id()
        return res

    # --- Utilidades ---
    def _extract_order_by_title(self):
        """Intenta encontrar una SO por su nombre dentro del título."""
        for rec in self:
            if rec.sale_link_id or not rec.name:
                continue
            for token in ORDER_NAME_RE.findall(rec.name.upper()):
                so = self.env["sale.order"].search([("name", "=", token)], limit=1)
                if so:
                    rec.sale_link_id = so.id
                    break

    def _copy_from_existing_sale_m2o(self):
        """Si el ticket ya tiene algún M2O a sale.order (cualquiera), lo copiamos."""
        m2o_fields = [
            f for f in self._fields.values()
            if isinstance(f, fields.Many2one) and f.comodel_name == "sale.order" and f.name != "sale_link_id"
        ]
        if not m2o_fields:
            return
        for rec in self:
            if rec.sale_link_id:
                continue
            for f in m2o_fields:
                val = rec[f.name]
                if val:
                    rec.sale_link_id = val.id
                    break

    def _sync_sale_link_id(self):
        """Rutina robusta: copia desde cualquier M2O existente o intenta deducir por el título."""
        self._copy_from_existing_sale_m2o()
        self._extract_order_by_title()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    helpdesk_ticket_ids = fields.One2many(
        "helpdesk.ticket", "sale_link_id", string="Tickets de Helpdesk"
    )
    helpdesk_ticket_count = fields.Integer(
        string="Nº Tickets",
        compute="_compute_helpdesk_ticket_count",
        store=False,
    )

    def _compute_helpdesk_ticket_count(self):
        for rec in self:
            rec.helpdesk_ticket_count = len(rec.helpdesk_ticket_ids)

    def action_view_helpdesk_tickets(self):
        """Abre la acción de tickets filtrada por esta venta."""
        self.ensure_one()
        action = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[0]
        action["domain"] = [("sale_link_id", "=", self.id)]
        action["context"] = {"default_sale_link_id": self.id}
        action["display_name"] = "Tickets de Helpdesk"
        return action