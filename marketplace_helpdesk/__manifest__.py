{
    "name": "Marketplace Helpdesk",
    "version": "1.0",
    "category": "Helpdesk",
    "summary": "Gestión de tickets de marketplaces como Mirakl, MediaMarkt, etc.",
    "author": "CFON Telecomunicaciones",
    "depends": ["base", "helpdesk"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/marketplace_account_views.xml",
        "views/marketplace_ticket_views.xml",
        "views/menu.xml"
    ],
    "application": True,
    "installable": True,
}
