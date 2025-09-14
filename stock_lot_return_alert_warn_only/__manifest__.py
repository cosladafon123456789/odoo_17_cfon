# -*- coding: utf-8 -*-
{'name': "Serial Return Alert (Warn Only)",
'summary': "Show warnings when a serial/lot exceeded return threshold; create activities (no blocking).",
'version': "17.0.1.1.0",
'category': "Inventory/Inventory",
'author': "ChatGPT",
'website': "https://example.com",
'license': "LGPL-3",
'depends': ["stock", "mail"],
'data': ["security/ir.model.access.csv", "views/res_config_settings_views.xml", "views/stock_lot_views.xml", "data/cron.xml"],
'installable': true,
'application': false}
