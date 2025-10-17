# -*- coding: utf-8 -*-
{
    "name": "CF Productividad Report (Patch 3)",
    "summary": "Informe de productividad (vista limpia, cache-safe)",
    "version": "17.0.0.3",
    "category": "Inventory/Reporting",
    "application": False,
    "license": "OEEL-1",
    "depends": ["base", "stock", "repair", "helpdesk", "cf_productivity_report"],
    "data": [
        "views/menu_productivity.xml",
        "views/productivity_full_stats_views.xml",
        "views/productivity_ticket_daily_views.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True
}
