{
    "name": "Marketplaces Helpdesk",
    "summary": "Tickets de marketplaces (base) con vistas y menús",
    "description": "Módulo base para gestionar tickets de marketplaces. Incluye modelos, vistas, menús y filtros ‘No leídos’/‘Todos’. Sin cron ni ajustes.",
    "author": "CFON",
    "category": "Helpdesk",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "application": True,
    "depends": ["base", "mail"],
   "data": [
    "security/security.xml",
    "security/ir.model.access.csv",
    "views/menu.xml",
    "views/marketplace_account_views.xml",
    "views/marketplace_ticket_views.xml",
],
}
