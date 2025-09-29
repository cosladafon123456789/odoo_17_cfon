
# -*- coding: utf-8 -*-
{
    'name': 'CFON - Motivo previo al reembolso en Pedido de Venta',
    'summary': 'Muestra un wizard para capturar el motivo antes de abrir el asistente estándar de reembolso/devolución',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'author': 'CFON / ChatGPT',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/refund_reason_wizard_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
