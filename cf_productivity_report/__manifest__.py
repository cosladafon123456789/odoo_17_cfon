{
    "name": "Informe de productividad (dashboard v2)",
    "summary": "Dashboard agrupado Día → Tipo → Usuario. Registra tickets (mensaje/cambio etapa) y excluye OdooBot.",
    "version": "17.0.1.4.0",
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