# -*- coding: utf-8 -*-
{
    "name": "CF Inventory Serial Import",
    "summary": "Importar IMEIs/Números de serie en pickings desde un wizard, validando que existan y estén en WH/Stock",
    "version": "17.0.1.0.0",
    "author": "CosladaFon + ChatGPT",
    "website": "https://cosladafon.com",
    "category": "Inventory/Inventory",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_views.xml",
        "views/serial_import_wizard_views.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False,
}