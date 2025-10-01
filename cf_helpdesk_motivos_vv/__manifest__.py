{
    'name': 'CF Helpdesk Motivos',
    'version': '17.0.3.0',
    'summary': 'Gestión de motivos de devolución en Helpdesk',
    'description': 'Añade un campo motivo de devolución, obligatorio en ciertas etapas y disponible en informes con menú independiente.',
    'author': 'CosladaFon',
    'depends': ['helpdesk'],
    'data': [
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_ticket_reports.xml',
    ],
    'installable': True,
    'application': False,
}
