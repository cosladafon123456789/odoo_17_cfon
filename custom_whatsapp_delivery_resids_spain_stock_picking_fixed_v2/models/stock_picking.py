from odoo import models, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def button_validate(self):
        res = super().button_validate()

        for picking in self:
            # Solo envía WhatsApp en salidas reales de venta,
            # no en devoluciones de proveedores ni movimientos desde compras
            if (
                picking.picking_type_code == 'outgoing'
                and not picking.purchase_id
                and (not picking.origin or not picking.origin.startswith('PO'))
            ):
                partner = picking.partner_id
                if partner and partner.country_id and partner.country_id.name == "España":
                    template = self.env['whatsapp.template'].search([
                        ('template_name', '=', 'factura_validada'),
                        ('model', '=', 'stock.picking')
                    ], limit=1)

                    if not template:
                        picking.message_post(body="⚠️ No se encontró la plantilla WhatsApp 'factura_validada'.")
                        continue

                    number = partner.mobile or partner.phone
                    if not number:
                        picking.message_post(body="⚠️ No hay número de teléfono para enviar WhatsApp.")
                        continue

                    try:
                        composer = self.env['whatsapp.mail.compose.message'].with_context(
                            active_model='stock.picking',
                            active_id=picking.id
                        ).create({
                            'wa_template_id': template.id,
                            'phone': number,
                            'res_model': 'stock.picking',
                            'res_ids': str(picking.id),
                        })
                        composer.action_send_whatsapp_template()
                        picking.message_post(body=f"✅ WhatsApp enviado a {partner.name} ({number})")
                    except Exception as e:
                        picking.message_post(body=f"⚠️ Error enviando WhatsApp: {str(e)}")
        return res