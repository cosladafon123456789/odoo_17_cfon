{
    "name": "CF Employee Productivity",
    "summary": "Dashboard y métricas de productividad por empleados: pedidos, reparaciones y tickets",
    "version": "17.0.1.0.0",
    "category": "Productivity",
    "author": "CFON Telecomunicaciones",
    "license": "LGPL-3",
    "depends": ["base", "board", "stock", "repair", "helpdesk", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/productivity_menu.xml",
        "views/productivity_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/repair_reason_wizard_views.xml"
    ],
    "application": True,
    "installable": True
}
