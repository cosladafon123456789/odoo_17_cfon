from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    marketplace_api_url = fields.Char(string='URL API Mirakl')
    marketplace_api_key = fields.Char(string='API Key Mirakl')

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update({
            'marketplace_api_url': self.env['ir.config_parameter'].sudo().get_param('marketplace_helpdesk.api_url', ''),
            'marketplace_api_key': self.env['ir.config_parameter'].sudo().get_param('marketplace_helpdesk.api_key', ''),
        })
        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('marketplace_helpdesk.api_url', self.marketplace_api_url or '')
        self.env['ir.config_parameter'].sudo().set_param('marketplace_helpdesk.api_key', self.marketplace_api_key or '')
