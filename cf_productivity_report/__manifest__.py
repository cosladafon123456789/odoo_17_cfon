{
    "name": "Informe de productividad (tickets v2)",
    "summary": "Añade registro al cambiar la etapa de un ticket",
    "version": "17.0.1.2.0",
    "author": "CosladaFon",
    "category": "Productivity",
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