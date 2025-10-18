{
    "name": "Productividad CF",
    "summary": "Productividad por usuario: Reparaciones, Tickets y Entregas (CosladaFon)",
    "version": "17.0.1.0.1",
    "author": "CosladaFon",
    "category": "Productivity",
    "depends": ["base", "mail", "repair", "helpdesk", "stock", "base_setup"],
    "data": [
        "views/productivity_views.xml",
        "views/menu_productivity.xml",
        "views/productivity_tickets_views.xml",
        "security/ir.model.access.csv"
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3"
}