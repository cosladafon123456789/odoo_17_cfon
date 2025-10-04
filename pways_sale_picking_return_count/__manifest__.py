# -*- coding: utf-8 -*-
{
    'name': 'Pways Sale Order Return Count',
    'version': '17.0',
    'summary': """Sale Order Return Count. 03/10/2025-rmu""",
    'description': """ Sale Order Shipment""",
    'category': 'Sale Order',
    'author':'Preciseways',
    'depends': ['sale_management', 'sale_stock','pways_repair_parts'],
    'data': [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/inherit_stock_lot_view.xml",
        "wizard/serial_scrap_wizard_views.xml",
    ],
    'installable': True,
    'application': True,
    'price': 0.0,
    'currency': 'EUR',
    'images':['static/description/banner.png'],
    'license': 'OPL-1',
}
