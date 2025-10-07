{
    "name": "Marketplaces",
    "summary": "Integración de mensajes de Marketplaces (Mirakl, MediaMarkt, etc.) con Odoo Helpdesk",
    "version": "17.0.1.0",
    "author": "CosladaFon",
    "category": "Helpdesk",
    "depends": ["base", "mail", "helpdesk"],
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/marketplace_account_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu.xml",
        "views/marketplace_ticket_views.xml",  # ⬅ se carga al final
        "data/ir_cron.xml",
    ],
    "installable": True,
    "application": True,
}
