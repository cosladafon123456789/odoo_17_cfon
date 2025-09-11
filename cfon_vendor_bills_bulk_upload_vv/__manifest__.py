# -*- coding: utf-8 -*-
{
    'name': 'CFON - Subir facturas proveedor (PDF)',
    'version': '17.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'ChatGPT for CFON',
    'website': 'https://www.cosladafon.com',
    'summary': 'Botón "Subir facturas" para arrastrar PDFs y crear borradores de facturas proveedor',
    'category': 'Accounting/Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],
    'assets': {},  # no assets needed
    'installable': True,
    'application': False,
}
