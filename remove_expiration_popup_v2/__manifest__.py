# -*- coding: utf-8 -*-
{
    'name': 'Remove Expiration Popup',
    'version': '17.0.1.0.1',
    'summary': 'Elimina el aviso de caducidad al validar entregas',
    'description': 'Deshabilita la comprobación de caducidad en albaranes/series para evitar el popup de confirmación.',
    'category': 'Inventory',
    'author': 'Cosladafon',
    'website': 'https://www.cosladafon.com',
    'depends': ['stock'],  # no exigimos product_expiry para evitar bloqueos si no está instalado
    'data': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}