{
    "name": "CF Productivity",
    "version": "17.0.2.0.0",
    "category": "Repair",
    "summary": "Informe/Configuración de productividad (menú en Reparaciones → Informe)",
    "author": "CFON Telecomunicaciones",
    "license": "LGPL-3",
    "depends": ["base", "repair", "mail"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/productivity_menu.xml",
        "security/ir.model.access.csv"
    ],
    "images": ["static/description/icon.png"],
    "application": False,
    "installable": True
}