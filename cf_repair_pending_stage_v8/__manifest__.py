{
    'name': 'CF Repair Pending Stage',
    'version': '17.0.1.7',
    'summary': 'Añade estado y botón "Pendiente de pieza". Incluye filtro global sin depender de XMLIDs variables.',
    'depends': ['repair'],
    'data': [
        'views/repair_order_view.xml',
        'data/repair_filters.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False
}
