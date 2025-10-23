{
    'name': 'CF Stock BAT100',
    'version': '17.0.2.0.0',
    'summary': 'Añade campo BAT100 a números de serie y movimientos de stock',
    'author': 'CosladaFon',
    'website': 'https://www.cosladafon.com',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        'views/stock_lot_views.xml',
        'views/stock_move_line_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}