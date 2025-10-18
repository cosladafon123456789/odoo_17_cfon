{
    "name": "Informe de productividad (tiempo medio)",
    "summary": "Añade tiempo medio entre las 20 primeras validaciones de cada usuario",
    "version": "17.0.1.1.0",
    "author": "CosladaFon",
    "category": "Inventory",
    "depends": ["base", "mail", "repair", "helpdesk", "stock", "base_setup"],
    "data": [
        "views/productivity_views.xml",
        "views/menu_productivity.xml",
        "security/ir.model.access.csv"
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3"
}