{
    "name": "Informe de productividad",
    "summary": "Informe de productividad por usuario: reparaciones, tickets y entregas",
    "version": "17.0.1.0.4",
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