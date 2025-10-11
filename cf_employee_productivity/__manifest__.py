{
    "name": "CF Productividad",
    "version": "1.0",
    "category": "Productivity",
    "summary": "Control de productividad de empleados (pedidos, reparaciones y postventa)",
    "author": "CFON Telecomunicaciones",
    "website": "https://cosladafon.com",
    "depends": ["base", "stock", "repair", "helpdesk"],
    "data": [
        "security/ir.model.access.csv",
        "views/productivity_views.xml",
        "views/res_config_settings_views.xml",
        "data/ir_cron.xml"
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
    "images": ["static/description/icon.png"]
}
