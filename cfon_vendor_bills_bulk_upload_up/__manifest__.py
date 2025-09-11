# -*- coding: utf-8 -*-
{
    'name': 'CFON - Subir facturas proveedor (PDF)',
    'version': '17.0.1.0.6',
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
        'views/actions.xml',
        'views/server_action.xml',
        
    ],
    
    'assets': {
        'web.assets_backend': [
            'cfon_vendor_bills_bulk_upload/static/src/js/add_list_button.js',
            'cfon_vendor_bills_bulk_upload/static/src/css/style.css',
        ],
    },
  # no assets needed
    'installable': True,
    'application': False,
}
