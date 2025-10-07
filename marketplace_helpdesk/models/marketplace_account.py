from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace (Mirakl)"

    name = fields.Char(required=True)
    base_url = fields.Char(string="Base URL", required=True, help="Ej: https://mediamarktsaturn.mirakl.net")
    api_key = fields.Char(string="API Key", required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    last_sync = fields.Datetime(string="Última sincronización", readonly=False, default=lambda self: fields.Datetime.now())
    sync_unread_only = fields.Boolean(string="Solo no leídos", default=True)
    note = fields.Text()

    def _normalized_base(self):
        self.ensure_one()
        url = (self.base_url or "").strip().rstrip("/")
        if url.endswith("/api"):
            url = url[:-4]
        return url

    def action_test_connection(self):
        for acc in self:
            client = self.env["mirakl.client"].with_context(company_id=acc.company_id.id)
            ok, info = client.test_connection(acc)
            if not ok:
                raise UserError(_("Conexión fallida: %s") % (info or _("sin detalle")))
        return True
