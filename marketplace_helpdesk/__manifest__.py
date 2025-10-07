{
    "name": "Marketplaces",
    "summary": "Tickets de mensajes de marketplaces (Mirakl) tipo Helpdesk",
    "version": "17.0.1.0.0",
    "author": "CosladaFon + ChatGPT",
    "website": "https://cosladafon.com",
    "license": "LGPL-3",
    "category": "Helpdesk",
    "depends": ["mail", "base"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/marketplace_ticket_views.xml",
        "views/marketplace_account_views.xml",
        "views/res_config_settings_views.xml",
        "data/ir_cron.xml"
    ],
    "assets": {},
    "application": True,
    "installable": True,
}
