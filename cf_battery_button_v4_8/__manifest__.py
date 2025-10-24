{
    'name': 'CF Battery Button v4.8',
    'version': '1.0',
    'author': 'CosladaFon',
    'category': 'Inventory',
    'summary': 'Botón Batería 100% en Lotes y Movimientos de Stock',
    'description': "Agrega un campo de tipo toggle 'Batería 100%' que se puede marcar tanto desde el popup de movimiento de stock como desde la vista de lotes. El estado se guarda automáticamente en el lote vinculado.",
    'depends': ['stock'],
    'data': [
        'views/stock_lot_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
