
# Serial Return Alert v1.2 (Safe, sin vistas)

Este paquete **no** hereda ninguna vista (cero XML de formularios), solo:
- Añade campos calculados al modelo `stock.lot` (veces devuelto, stock interno, alerta).
- Crea un **menú y acción** para listar lotes con 2+ devoluciones y stock.

## Uso
Inventario → Trazabilidad → **SN/Lotes en stock +2 dev**

## Si persiste la pantalla en blanco
- El problema no lo está causando una herencia de vistas de este módulo (porque no hay). 
- Revisa el log del servidor: puede ser otro módulo o un asset corrupto.
- Prueba a **actualizar base** desde CLI:
  ```bash
  odoo-bin -d TU_BD -u base --stop-after-init
  ```
- Borra caché de assets del despliegue y reinicia el servicio.
