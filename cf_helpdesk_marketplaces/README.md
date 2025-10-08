
# Marketplace Helpdesk (Odoo 17)

Centraliza los mensajes de marketplaces (ej. Mirakl) en un módulo tipo Helpdesk. Permite:
- Conectar múltiples cuentas/API.
- Descargar hilos/mensajes y crear tickets.
- Responder desde Odoo (wizard) devolviendo al marketplace.
- Cron de sincronización cada 5 minutos.
- Chatter y actividades.

## Configuración
1. Ajusta `API Base URL`, `API Key` y `Shop ID` (si aplica).
2. Usa el botón **Sincronizar ahora** para una primera carga.
3. Responde desde el ticket con **Responder**.

> Nota: Los endpoints exactos pueden variar entre marketplaces Mirakl. Adapta `marketplace_account._api_get/_api_post` y las rutas `/api/messages` y `/api/messages/reply` a tu plataforma concreta.
