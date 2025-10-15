{
    'name': 'CF Repair Pending Stage (Odoo 17 Enterprise)',
    'version': '17.0.2.1',
    'summary': 'Añade estado y botones para "Pendiente de pieza" (compatible OWL).',
    'depends': ['repair'],
    'data': [
        'views/repair_order_view.xml',
        'data/repair_filters.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False
}
