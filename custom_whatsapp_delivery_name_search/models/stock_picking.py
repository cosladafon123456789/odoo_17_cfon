from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.picking_type_code == 'outgoing':
                try:
                    # Buscar plantilla por nombre técnico (template_name)
                    template = self.env['whatsapp.template'].search([('template_name', '=', 'factura_validada')], limit=1)
                    if template and (picking.partner_id.phone or picking.partner_id.mobile):
                        number = picking.partner_id.phone or picking.partner_id.mobile
                        template.send_message(number, picking)
                except Exception as e:
                    _logger = self.env['ir.logging']
                    _logger.create({
                        'name': 'WhatsApp Delivery',
                        'type': 'server',
                        'level': 'error',
                        'dbname': self._cr.dbname,
                        'message': str(e),
                        'path': 'stock_picking',
                        'line': 'button_validate',
                        'func': 'button_validate',
                    })
        return res
