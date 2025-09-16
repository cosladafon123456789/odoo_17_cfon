
# Serial Return Alert (Odoo 17)

Módulo ligero que:
- Calcula cuántas veces un número de serie/lote ha sido devuelto por clientes (albaranes de retorno finalizados).
- Muestra banner de alerta si el lote acumula 2 o más devoluciones.
- Añade menú **Inventario → Trazabilidad → SN/Lotes en stock +2 dev** para ver los que están en stock interno y con 2+ devoluciones.
- Muestra un aviso NO intrusivo en el formulario de albarán si incluye lotes con alerta (no abre pop-ups ni bloquea).

### Instalación
1. Subir la carpeta `cfon_serial_return_alert` a tus addons.
2. Activar modo desarrollador, **Actualizar lista de aplicaciones**, e instalar.
3. Requiere app **Inventario** (`stock`).

### Notas técnicas
- El cómputo usa SQL para ser eficiente.
- Se consideran devoluciones: `stock.picking.is_return = True`, `state = 'done'`, `picking_type.code = 'incoming'`.
- Stock interno via `stock_quant` en ubicaciones `usage = 'internal'`.
- Umbral fijo de 2 (puedes cambiar `RETURN_THRESHOLD` en `models/stock_lot.py`).

