# -*- coding: utf-8 -*-
{'name': "CFON Serial Return Alerts",
'summary': "Warn and log activities when a serial/lot is returned to stock more than N times (no blocking).",
'version': "17.0.1.0.0",
'category': "Inventory/Inventory",
'author': "CFON / CosladaFon",
'website': "https://cosladafon.com",
'license': "LGPL-3",
'depends': ["stock", "mail"],
'data': ["security/ir.model.access.csv", "views/res_config_settings_views.xml", "views/stock_lot_views.xml", "data/cron.xml"],
'assets': {},
'installable': true,
'application': false}
