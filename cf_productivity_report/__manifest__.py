{
    "name": "Productividad CF",
    "summary": "Productividad por usuario: reparaciones, tickets y validaciones con dashboard",
    "version": "17.0.3.0.0",
    "author": "CosladaFon",
    "category": "Productivity",
    "depends": ["base", "mail", "repair", "helpdesk", "stock", "base_setup"],
    "data": [
        "views/productivity_views.xml",
        "views/menu_productivity.xml",
        "views/company_productivity_views.xml",
        "views/repair_reason_wizard_views.xml",
        "views/dashboard_views.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": True,
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook"
}
