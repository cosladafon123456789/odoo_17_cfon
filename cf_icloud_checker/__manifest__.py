{
    "name": "Comprobador de iCloud (CosladaFon)",
    "version": "1.0",
    "summary": "Botón para comprobar el estado de iCloud en los números de serie (Odoo 17 Enterprise)",
    "category": "Inventory",
    "author": "CosladaFon",
    "depends": ["stock"],
    "data": ["views/stock_lot_views.xml"],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
    "external_dependencies": {"python": ["requests", "bs4"]},
}