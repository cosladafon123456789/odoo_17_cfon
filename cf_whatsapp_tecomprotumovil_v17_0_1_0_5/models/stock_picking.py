from odoo import models, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        for picking in self:
            # Solo para Recepciones
            if picking.picking_type_id.code != 'incoming':
                continue

            purchase = picking.purchase_id
            if purchase and purchase.x_studio_comprado:
                partner = purchase.partner_id
                phone = partner.phone or partner.mobile
                if not phone:
                    continue

                # Buscar plantilla y cuenta
                template = self.env['whatsapp.template'].search([('name', '=', 'tecomprotumovil')], limit=1)
                wa_account = self.env['whatsapp.account'].search([], limit=1)

                if template and wa_account:
                    # Crear mensaje de WhatsApp
                    msg = self.env['whatsapp.message'].create({
                        'mobile_number': phone,
                        'wa_template_id': template.id,
                        'wa_account_id': wa_account.id,
                        'message_type': 'structured',
                        'state': 'queued',
                    })

                    # Enviar mensaje automáticamente
                    try:
                        msg._send_message()
                        picking.message_post(
                            body="📲 Se ha enviado automáticamente el mensaje de WhatsApp “tecomprotumovil” al proveedor."
                        )
                    except Exception as e:
                        picking.message_post(
                            body=f"⚠️ Error al enviar mensaje de WhatsApp automático: {str(e)}"
                        )

        return res
