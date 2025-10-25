{
    'name': 'CF Battery Button v4.9',
    'version': '1.0',
    'author': 'CosladaFon',
    'category': 'Inventory',
    'summary': 'Botón Batería 100% en Lotes, Movimientos de Stock y Ubicaciones',
    'description': """
Este módulo agrega un campo tipo toggle 'Batería 100%' que se puede marcar tanto desde el popup
de movimiento de stock como desde la vista de lotes. 
El estado se guarda automáticamente en el lote vinculado y se muestra también en el panel de ubicaciones (vista Kanban).
    """,
    'depends': ['stock'],
    'data': [
        'views/stock_lot_views.xml',       # contiene vistas de lotes y herencia de kanban de stock.quant
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
