{
    "name": "CF Productivity",
    "version": "17.0.1.0.0",
    "category": "Productivity",
    "summary": "Dashboard, métricas y configuración de productividad (sin cron)",
    "author": "CFON Telecomunicaciones",
    "license": "LGPL-3",
    "depends": ["base", "stock", "repair", "helpdesk", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/productivity_menu.xml",
        "views/productivity_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/repair_reason_wizard_views.xml"
    ],
    "images": ["static/description/icon.png"],
    "application": True,
    "installable": True
}