{
    'name': 'CF Repair Pending Stage',
    'version': '17.0.1.8',
    'summary': 'Añade estado, botón y filtro "Pendiente de pieza" en Reparaciones.',
    'depends': ['repair'],
    'data': [
        'views/repair_order_view.xml',
        'data/repair_filters.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False
}
