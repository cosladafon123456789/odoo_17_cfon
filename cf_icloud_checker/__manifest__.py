{
    "name": "Comprobador de iCloud (CosladaFon)",
    "version": "1.4.0",
    "summary": "Comprueba iCloud (ON/OFF) en imeicheck.net siguiendo redirecciones – Odoo 17",
    "category": "Inventory",
    "author": "CosladaFon",
    "depends": ["stock"],
    "data": ["views/stock_lot_views.xml"],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
    "external_dependencies": {"python": ["requests", "bs4"]}
}
