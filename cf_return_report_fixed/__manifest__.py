# -*- coding: utf-8 -*-
{
    "name": "CF Return Report",
    "summary": "Informe de devoluciones con KPIs y wizard de motivo al recibir",
    "version": "17.0.1.0.0",
    "author": "CosladaFon (CFON)",
    "license": "LGPL-3",
    "website": "https://www.cosladafon.com",
    "category": "Inventory/Inventory",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/cf_return_reason_data.xml",
        "views/cf_return_dashboard_views.xml",
        "views/stock_picking_inherit_views.xml",
        "wizard/return_reason_wizard_views.xml",
        "views/menu.xml",
    ],
    "assets": {},
    "application": False,
    "installable": True,
}
