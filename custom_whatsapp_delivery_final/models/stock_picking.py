from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.picking_type_code == 'outgoing':
                try:
                    # Buscar plantilla por nombre técnico
                    template = self.env['whatsapp.template'].search(
                        [('template_name', '=', 'factura_validada')], limit=1
                    )
                    if not template:
                        continue

                    number = picking.partner_id.phone or picking.partner_id.mobile
                    if not number:
                        continue

                    # Crear el composer
                    composer = self.env['whatsapp.composer'].create({
                        'template_id': template.id,
                        'phone': number,
                        'res_id': picking.id,
                        'res_model': 'stock.picking',
                    })

                    # Ejecutar acción de envío
                    composer.action_send_whatsapp_template()

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
