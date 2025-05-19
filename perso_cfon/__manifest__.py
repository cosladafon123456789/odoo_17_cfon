# -*- coding: utf-8 -*-
{
    'name': "Perso Cfon",

    'summary': """Módulo Personalizado para Cfon Telecomunicaciones S.L. """,

    'description': """
        
        Nanobytes - Personalización para CFON TELECOMUNICACIONES S.L.
        
        This module was made by Nanobytes Informatica y Telecomunicaciones S.L,
        for more information, contact us : http://nanobytes.es
        * GAP V1 : REBU . Necesario rellenar el campo diario REBU en la configuracion
        
    """,

    'author': "Nanobytes Informatica y Telecomunicaciones S.L",
    'category': 'custom',
    'version': '1.0',
    'depends': ['base', 'product', 'sale', 'sale_management', 'stock', 'account', 'account_accountant', 'l10n_es', 'sale_stock'],
    'installable': True,
    'application': False,
    'data': [
        #GAP V1
        'data/new_tax_data.xml',
        'data/mod303.xml',
        'data/mod390.xml',
        'views/product_views.xml',
        'views/stock_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_views.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
    ],
    'assets': {
    } 
}
