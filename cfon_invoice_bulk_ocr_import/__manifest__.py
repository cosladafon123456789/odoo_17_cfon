{
    "name": "CFON Invoice Bulk OCR Import",
    "summary": "Arrastra y suelta facturas (PDF/JPG/PNG) para crear facturas automáticamente con OCR.",
    "version": "17.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "ChatGPT for CosladaFon",
    "website": "https://www.cosladafon.com",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": ["security/ir.model.access.csv", "views/invoice_import_views.xml"],
    "assets": {"web.assets_backend": ["cfon_invoice_bulk_ocr_import/static/src/js/drop_import.js", "cfon_invoice_bulk_ocr_import/static/src/css/drop_import.css"]},
    "installable": true,
    "application": false
}