# -*- coding: utf-8 -*-
{
    "name": "Vendor Bills: OCR Upload",
    "summary": "Botón 'Subir con OCR' para crear facturas proveedor en borrador desde PDFs.",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "author": "ChatGPT for CosladaFon",
    "license": "LGPL-3",
    "depends": ["account", "base"],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/bill_ocr_upload_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cf_vendor_bill_ocr_upload/static/src/js/bill_ocr_button.js",
        ]
    },
    "external_dependencies": {"python": ["pdfminer.six"]},
    "installable": True,
}
