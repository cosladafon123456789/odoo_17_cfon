{
    "name": "Comprobador de iCloud (CosladaFon)",
    "version": "1.2.0",
    "summary": "Botón para comprobar el estado de iCloud (ON/OFF) en los números de serie / IMEI – Odoo 17",
    "category": "Inventory",
    "author": "CosladaFon",
    "depends": ["stock"],
    "data": ["views/stock_lot_views.xml"],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
    "external_dependencies": {"python": ["requests", "bs4"]}
}
