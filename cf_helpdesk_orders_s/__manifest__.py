{
    'name': 'CF Helpdesk Orders',
    'version': '1.0',
    'summary': 'Smartbutton para ver tickets Helpdesk desde pedidos de venta',
    'description': """
        Muestra un smartbutton en los pedidos de venta que permite ver los 
        tickets de Helpdesk relacionados cuyo nombre contiene el número de pedido.
    """,
    'author': 'CosladaFon',
    'website': 'https://www.cosladafon.com',
    'category': 'Sales',
    'depends': ['sale_management', 'helpdesk'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}