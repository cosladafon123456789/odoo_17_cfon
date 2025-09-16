
# Serial Return Alert v1.1 (Odoo 17)

Versión segura con herencias de vistas conservadoras (evita `position="before"`).

## Emergencia: página en blanco
1. **Revisar log del servidor** para ver el traceback.
2. Para desactivar sólo las vistas del módulo desde SQL (sin desinstalar):
```sql
-- Desactivar vistas problemáticas del módulo
UPDATE ir_ui_view
SET active = false
WHERE id IN (
  SELECT res_id
  FROM ir_model_data
  WHERE module = 'cfon_serial_return_alert'
    AND model = 'ir.ui.view'
);
```
3. **Actualizar assets** (si procede) y reiniciar Odoo.
4. Luego puedes actualizar el módulo con esta v1.1.

