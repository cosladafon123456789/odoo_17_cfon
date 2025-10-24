# -*- coding: utf-8 -*-
{
    "name": "CF Battery Status",
    "version": "17.0.1.2.0",
    "summary": "Añade botón BAT100 en números de serie/lote",
    "author": "CosladaFon + ChatGPT",
    "license": "LGPL-3",
    "category": "Inventory/Inventory",
    "depends": ["stock", "stock_lot"],  # 🔹 importante: Odoo 17 separa el modelo aquí
    "data": [
        "security/ir.model.access.csv",
        "views/stock_production_lot_views.xml",
    ],
    "installable": True,
    "application": False,
}
