
# CFON OCA Invoice OCR Bridge (Odoo 17)

Extensión que **aprovecha la familia OCA `account_invoice_import`** para crear facturas de proveedor en **borrador**, añadiendo:

- **OCR local** (Tesseract) para **PDF escaneados e imágenes** (JPG/PNG).
- **Importación masiva** (multi-archivo) con una sola acción.
- **Autocreación de proveedor** por NIF/CIF (opcional).
- Guardado de **texto OCR** en la factura para auditoría.

Si está instalado `account_invoice_import` (OCA), el puente **intenta delegar** al importador de OCA cuando el PDF contiene texto (no escaneo). Si no está, o si el documento no es soportado, **hace fallback** a un parser heurístico interno.
