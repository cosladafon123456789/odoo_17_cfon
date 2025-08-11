# mail_message_truncate_lazy (Odoo 17)

Trunca de forma segura los mensajes largos en Discuss/chatter usando `<details>/<summary>`.
- No bloquea el arranque (assets *lazy*).
- Umbral configurable por parámetro del sistema `mail_message_truncate.threshold` (por defecto 500).

## Instalación
1. Copiar a la ruta de addons y actualizar lista de apps.
2. Instalar **Truncar mensajes largos (carga diferida, seguro)**.

## Notas
- Solo envuelve el cuerpo del mensaje si supera el umbral.
- Sin dependencias ni parches a plantillas OWL.
