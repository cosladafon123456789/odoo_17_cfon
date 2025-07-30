# -*- coding: utf-8 -*-
{
    'name': 'PWays Sale Order Shipment',
    'version': '17.0',
    'summary': """Sale Order Shipment. 30/07/2025""",
    'description': """ Sale Order Shipment""",
    'category': 'Sale Order',
    'author':'Preciseways',
    'depends': ['sale_management', 'delivery_stock_picking_batch', 'stock'],
    'data': [
        'views/inherit_stock_move_view.xml',
        'views/sale_order_line_view.xml',
        'report/report_action.xml',
        'report/serial_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'price': 0.0,
    'currency': 'EUR',
    'images':['static/description/banner.png'],
    'license': 'OPL-1',
}
