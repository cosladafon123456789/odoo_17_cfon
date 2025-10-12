{
    "name": "Productividad CF",
    "version": "1.0",
    "category": "Productividad",
    "summary": "Control de productividad (Reparaciones, Tickets, Ventas)",
    "author": "CosladaFon",
    "depends": ["base", "repair", "helpdesk", "stock", "base_setup"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/productivity_views.xml",
        "views/productivity_menu.xml",
        "views/company_productivity_views.xml",
        "views/res_config_settings_views.xml",
        "views/repair_reason_wizard_views.xml"
    ],
    "application": True,
    "installable": True
}
