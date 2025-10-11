{
    "name": "CF Productivity",
    "version": "17.0.1.1.0",
    "category": "Productivity",
    "summary": "Dashboard, métricas y configuración de productividad (sin cron)",
    "author": "CFON Telecomunicaciones",
    "license": "LGPL-3",
    "depends": ["base", "stock", "repair", "helpdesk", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/productivity_menu.xml"
    ],
    "images": ["static/description/icon.png"],
    "application": True,
    "installable": True,
}
