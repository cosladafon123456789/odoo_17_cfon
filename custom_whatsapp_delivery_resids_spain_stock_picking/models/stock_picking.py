from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.picking_type_code == 'outgoing':
                try:
                    # Solo enviar si el país del cliente es España
                    if picking.partner_id.country_id and picking.partner_id.country_id.name != "España":
                        continue

                    template = self.env['whatsapp.template'].search(
                        [('template_name', '=', 'factura_validada'),
                         ('model', '=', 'stock.picking')], limit=1
                    )
                    if not template:
                        picking.message_post(body="❌ No se encontró plantilla WhatsApp 'factura_validada' en stock.picking.")
                        continue

                    number = picking.partner_id.phone or picking.partner_id.mobile
                    if not number:
                        picking.message_post(body=f"❌ Cliente {picking.partner_id.name} sin teléfono/móvil.")
                        continue

                    # Normalizar número: si no empieza por +34, añadirlo
                    number = number.replace(" ", "").replace("-", "")
                    if not number.startswith("+34"):
                        if number.startswith("34"):
                            number = "+" + number
                        else:
                            number = "+34" + number.lstrip("0")

                    composer = self.env['whatsapp.composer'].with_context(
                        default_res_model='stock.picking',
                        search_default_model='stock.picking',
                        active_model='stock.picking',
                        active_id=picking.id
                    ).create({
                        'wa_template_id': template.id,
                        'phone': number,
                        'res_model': 'stock.picking',
                        'res_ids': str(picking.id),
                    })

                    composer.action_send_whatsapp_template()

                    picking.message_post(body=f"✅ WhatsApp enviado a {picking.partner_id.name} ({number})")

                except Exception as e:
                    picking.message_post(body=f"⚠️ Error enviando WhatsApp: {str(e)}")
        return res
