# Vendor Bills: OCR Upload (Odoo 17)
- Añade un botón **Subir con OCR** junto a *Subir* en el listado de Facturas de Proveedor.
- Abre un asistente donde puedes arrastrar múltiples PDFs.
- Lee datos básicos (proveedor, fecha, vencimiento, nº factura, totales) con `pdfminer.six` y crea borradores.
- Adjunta automáticamente el PDF a la factura creada.

## Dependencias
```
pip3 install pdfminer.six
```
(Requiere instalarlo en el entorno de Odoo).

## Instalación
1. Copia la carpeta `cf_vendor_bill_ocr_upload` a tus `addons`.
2. Actualiza apps y instala el módulo.
3. En **Contabilidad > Proveedores > Facturas**, verás el botón **Subir con OCR**.

## Limitaciones
- El parser es genérico; para mejores resultados, añade el CIF/NIF al partner.
- Si no se detectan líneas, crea 1 línea con el total para editar manualmente.
