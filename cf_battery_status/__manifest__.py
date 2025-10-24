# -*- coding: utf-8 -*-
{
    "name": "CF Battery Status",
    "version": "17.0.1.3.0",
    "summary": "Añade botón BAT100 en números de serie/lote",
    "author": "CosladaFon + ChatGPT",
    "license": "LGPL-3",
    "category": "Inventory/Inventory",
    "depends": ["stock"],  # ✅ Solo stock, tu entorno ya incluye lotes dentro
    "data": [
        "security/ir.model.access.csv",
        "views/stock_production_lot_views.xml",
    ],
    "installable": True,
    "application": False,
}
