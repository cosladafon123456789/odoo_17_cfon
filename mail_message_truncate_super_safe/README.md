# mail_message_truncate_super_safe (Odoo 17)

Trunca mensajes largos (más de 50 caracteres) en Conversaciones y Chatter con “... Ver más / Ver menos”.
- Ultra conservador: corre tras `window.load`, con `try/catch` en todo.
- Busca automáticamente el contenedor de texto y lo envuelve con `<details>/<summary>`.
- Carga en `web.assets_backend`, pero no ejecuta nada hasta que el cliente está listo.

Instalación:
1. Copia el módulo a tu ruta de addons.
2. Reinicia Odoo, **Update Apps List** e instala.
3. Limpia la caché del navegador (Ctrl+F5) o usa ventana privada.
