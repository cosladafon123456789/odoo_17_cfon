{
    'name': 'CF Stock BAT100',
    'version': '17.0.1.0.1',
    'summary': 'Casilla BAT100 junto a cada IMEI/serial en recepciones y entregas',
    'author': 'CosladaFon',
    'website': 'https://www.cosladafon.com',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        'views/stock_lot_views.xml',
        'views/stock_move_line_views.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}