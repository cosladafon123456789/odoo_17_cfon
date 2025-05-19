# -*- coding: utf-8 -*-
{
    'name': 'Odoo Shipping Partners',
    'version': '1.0',
    'summary': '',
    'category': 'Sales',

    'depends': ['stock_delivery', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/stock_picking_view.xml',
        'views/shipping_partner_view.xml',
        'views/delivery_carrier_view.xml',
        'views/shipping_api_log_view.xml',
    ],

    'images': ['static/description/base_shipping.jpg'],
    # Author
    'author': 'TeqStars',
    'website': 'http://teqstars.com/r/bSq',
    'support': 'support@teqstars.com',
    'maintainer': 'TeqStars',
    'demo': [],
    # 'qweb': ['static/src/xml/dashboard.backend.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 9.99,
    'currency': 'EUR',
}
