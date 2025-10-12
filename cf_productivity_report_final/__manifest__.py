{
    "name": "Control de Productividad CF",
    "summary": "Productividad por usuario: Reparaciones, Tickets y Entregas",
    "version": "17.0.1.0.0",
    "author": "CosladaFon",
    "website": "",
    "category": "Productivity",
    "depends": ["base", "mail", "repair", "helpdesk", "stock", "base_setup"],
    "data": [
        "security/ir.model.access.csv",
        "views/productivity_views.xml",
        "views/menu_productivity.xml",
        "views/company_productivity_views.xml",
        "views/repair_reason_wizard_views.xml"
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3"
}
