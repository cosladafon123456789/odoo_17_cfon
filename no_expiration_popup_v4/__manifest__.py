# -*- coding: utf-8 -*-
{
    'name': 'No Expiration Popup (v4)',
    'version': '17.0.1.0.0',
    'summary': 'Suprime totalmente el popup de caducidad en validaciones de stock',
    'description': 'Evita el asistente de caducidad: fuerza contexto en button_validate, anula _check_expiration_date en stock.move.line y neutraliza el wizard stock.warn.expiration si existe.',
    'category': 'Inventory/Stock',
    'author': 'Cosladafon',
    'website': 'https://www.cosladafon.com',
    'depends': ['stock', 'product_expiry'],
    'data': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
