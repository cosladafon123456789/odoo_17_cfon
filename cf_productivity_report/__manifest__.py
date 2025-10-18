{
    "name": "Informe de productividad (tickets v3 sin OdooBot)",
    "summary": "Evita que OdooBot genere registros de productividad",
    "version": "17.0.1.3.0",
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