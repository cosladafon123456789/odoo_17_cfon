
# CFON Invoice Bulk OCR Import (Odoo 17)

- Importación masiva por **arrastrar y soltar** de facturas (PDF/JPG/PNG).
- Extrae cabecera (nombre, NIF/CIF, número, fecha, total, moneda) y líneas cuando sea posible.
- Si no detecta líneas, crea una línea única con la base imponible.
- Empareja el proveedor por NIF/CIF. Si no existe, lo crea (opcional).
- Configurable: diario de proveedor, cuenta de gasto por defecto, creación automática de partner.

> **Nota**: La OCR usa `pytesseract` y requiere que el binario `tesseract` esté instalado en el servidor. Como fallback, si el PDF es texto, se usa `pdfplumber`/`pypdf`. Revisa `requirements.txt`.


## Dropzone (arrastrar & soltar) configurable
En Ajustes → Contabilidad puedes activar/desactivar:
- **Dropzone en Facturas de Proveedor** (activado por defecto)
- **Dropzone en Facturas de Cliente** (desactivado por defecto)
- **Dropzone en módulo Documentos** (activado por defecto)
