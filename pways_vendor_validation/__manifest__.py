# -*- coding: utf-8 -*-
{
    'name': "Vendor Validation",
    'summary': "Vendor Validation.",
    'description': "Vendor Validation.",
    'author' : 'Preciseways',
    'website': "http://www.preciseways.com",
    'category': 'Purchase',
    'version': '17.0',
    'depends': ['purchase', 'sale_management', 'sale_stock'],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/vendor_backlist_views.xml',
        'views/inherit_sale_order_views.xml',
    ],
    
    'installable': True,
    'application': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images':['static/description/banner.png'],

}
