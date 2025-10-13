{
    "name": "Productividad CF",
    "summary": "Productividad por usuario: Reparaciones, Tickets y Entregas (CosladaFon)",
    "version": "17.0.2.0.0",
    "author": "CosladaFon",
    "website": "",
    "category": "Productivity",
    "depends": ["base", "mail", "repair", "helpdesk", "stock", "base_setup"],
    "data": [
        "views/productivity_views.xml",
        "views/menu_productivity.xml",
        "views/company_productivity_views.xml",
        "views/repair_reason_wizard_views.xml",
        "security/ir.model.access.csv"
    ],
    "application": True,
    "installable": True,
}
