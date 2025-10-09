{
    "name": "Marketplace Helpdesk",
    "version": "17.0.2.0.0",
    "category": "Helpdesk",
    "summary": "Helpdesk unificado para marketplaces Mirakl (PCComponentes, MediaMarkt, etc.) con replies.",
    "author": "CFON Telecomunicaciones",
    "website": "https://cosladafon.com",
    "depends": ["base", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/marketplace_account_views.xml",
        "views/marketplace_ticket_views.xml",
        "views/menu.xml",
        "data/ir_cron.xml"
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3"
}