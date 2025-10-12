# -*- coding: utf-8 -*-
{
    "name": "CF Productividad - Reparaciones, Tickets y Pedidos",
    "summary": "Contabiliza productividad: reparaciones finalizadas (con motivos), tickets respondidos y entregas validadas. Dashboard estilo Devoluciones.",
    "version": "17.0.1.0.1",
    "author": "CFON Telecomunicaciones",
    "website": "https://cosladafon.com",
    "license": "LGPL-3",
    "depends": ["base", "mail", "sale_management", "stock", "helpdesk", "repair", "base_setup"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/productivity_views.xml",
        "views/repair_reason_wizard_views.xml",
        "views/productivity_menu.xml",
        "views/company_productivity_views.xml"
    ],
    "application": True,
    "installable": True,
}