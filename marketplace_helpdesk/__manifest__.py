{
    "name": "Marketplaces",
    "summary": "Sincroniza hilos de Mirakl como tickets (solo no leídos)",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "author": "ChatGPT Assist",
    "website": "https://example.com",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/marketplace_ticket_views.xml",
        "views/marketplace_account_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu.xml",
        "data/ir_cron.xml"
    ],
    "installable": True,
    "application": True
}
