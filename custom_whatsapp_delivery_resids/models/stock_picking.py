from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.picking_type_code == 'outgoing':
                try:
                    template = self.env['whatsapp.template'].search(
                        [('template_name', '=', 'factura_validada')], limit=1
                    )
                    if not template:
                        picking.message_post(body="❌ No se encontró plantilla WhatsApp con nombre 'factura_validada'.")
                        continue

                    number = picking.partner_id.phone or picking.partner_id.mobile
                    if not number:
                        picking.message_post(body=f"❌ Cliente {picking.partner_id.name} sin teléfono/móvil.")
                        continue

                    composer = self.env['whatsapp.composer'].with_context(
                        default_res_ids=str(picking.id),
                        default_res_model='stock.picking',
                        default_model='stock.picking',
                        search_default_model='stock.picking',
                        active_model='stock.picking',
                        active_id=picking.id
                    ).create({
                        'wa_template_id': template.id,
                        'phone': number,
                        'res_ids': str(picking.id),
                        'res_model': 'stock.picking',
                    })

                    composer.with_context(
                        default_model='stock.picking',
                        search_default_model='stock.picking',
                        active_model='stock.picking',
                        active_id=picking.id
                    ).action_send_whatsapp_template()

                    picking.message_post(body=f"📲 WhatsApp enviado automáticamente a {number} con plantilla {template.template_name}")

                except Exception as e:
                    picking.message_post(body=f"❌ Error al enviar WhatsApp: {e}")
        return res
