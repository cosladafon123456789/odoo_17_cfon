{
    "name": "CF Employee Productivity",
    "summary": "Aplicación Productividad: dashboard, métricas y correo diario",
    "version": "17.0.3.0.0",
    "category": "Productivity",
    "author": "CFON Telecomunicaciones",
    "license": "LGPL-3",
    "depends": ["base", "stock", "repair", "helpdesk", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/productivity_menu.xml",
        "views/productivity_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/repair_reason_wizard_views.xml",
        "data/ir_cron.xml"
    ],
    "images": ["static/description/icon.png"],
    "application": True,
    "installable": True
}
