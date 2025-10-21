
CF WhatsApp on Purchase Deliveries (Odoo 17)
============================================

Qué hace
--------
- Al **validar una entrega de compra** (picking tipo incoming) vinculada a un `purchase.order` con el booleano **x_studio_comprado = True**,
  envía automáticamente la plantilla WhatsApp **'tecomprotumovil'**.
- Marca la entrega con `cf_whatsapp_sent = True` y al **partner** con `cf_whatsapp_tecomprotumovil_sent = True` para **no reenviar** más veces al mismo cliente.

Requisitos
----------
- App oficial **WhatsApp** de Odoo 17 instalada y configurada.
- Plantilla de WhatsApp **'tecomprotumovil'** en estado **Aprobado**.
- El contacto debe tener teléfono/móvil (`mobile` o `phone`).

Notas
-----
- Si el envío falla, **no bloquea** la validación; deja un mensaje en el chatter de la entrega.
- Para volver a permitir un envío a un cliente concreto, desmarcar manualmente
  el campo *'WhatsApp TeComproTuMovil ya enviado'* en el contacto.

