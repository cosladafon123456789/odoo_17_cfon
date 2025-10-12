# -*- coding: utf-8 -*-
{
    "name": "Productividad CF",
    "summary": "Contabiliza productividad: reparaciones finalizadas (con motivos), tickets respondidos y entregas validadas. Dashboard estilo Devoluciones.",
    "version": "17.0.1.0.1",
    "author": "CFON Telecomunicaciones",
    "website": "https://cosladafon.com",
    "license": "LGPL-3",
    "depends": ["base", "base_setup", "repair", "helpdesk", "stock"],
    "data": [
        "security/security.xml",
        "views/repair_reason_wizard_views.xml",
        "views/productivity_views.xml",
        "views/productivity_menu.xml",
        "views/company_productivity_views.xml",
        "security/ir.model.access.csv"
    ],
    "application": True,
    "installable": True,
}