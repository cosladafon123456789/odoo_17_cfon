
# Serial Return Alert v1.4 (Safe, Odoo 17)

- Sin herencias de vistas.
- Hereda `stock.lot`.
- SQL robusto para contar devoluciones; fallback si no existe `stock_picking.is_return`.
- Menú: **Inventario → Trazabilidad → SN/Lotes en stock +2 dev**.

## Recuperación si algo fallara
Desactivar vistas y desinstalar por SQL:
```sql
UPDATE ir_ui_view
SET active = false
WHERE id IN (
  SELECT res_id FROM ir_model_data
  WHERE module IN ('cfon_serial_return_alert_v14_fixed') AND model = 'ir.ui.view'
);
UPDATE ir_module_module SET state = 'uninstalled'
WHERE name IN ('cfon_serial_return_alert_v14_fixed');
```
