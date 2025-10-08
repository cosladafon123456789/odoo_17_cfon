
# Marketplace Helpdesk (Odoo 17)

Centraliza mensajes de marketplaces (Mirakl) en un módulo tipo Helpdesk. Permite:
- Conectar una cuenta Mirakl (inicial).
- Descargar hilos/mensajes y crear tickets vinculados a `res.partner`.
- Responder desde Odoo (wizard) devolviendo al marketplace.
- Cron de sincronización cada 5 minutos.
- Logging detallado (en chatter + logs) y botón **Probar conexión**.

## Instalación (GitHub)
1. Copia la carpeta `cf_helpdesk_marketplaces` en tu repo de addons.
2. Reinicia Odoo y **Actualizar lista de aplicaciones**.
3. Instala **Marketplace Helpdesk**.

## Configuración
- En **Marketplace Helpdesk → Cuentas**: define `API Base URL`, `API Key`, `Shop ID` (si aplica).
- Usa **Probar conexión** para validar la API.
- Usa **Sincronizar ahora** para la primera importación.

> Ajusta las rutas `/api/messages` y `/api/messages/reply` si tu Mirakl usa endpoints diferentes.
