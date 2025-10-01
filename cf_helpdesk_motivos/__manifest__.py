{
    'name': 'CF Helpdesk Motivos',
    'version': '17.0.1.0',
    'summary': 'Gestión de motivos de devolución en Helpdesk',
    'description': 'Añade un campo motivo de devolución, obligatorio en ciertas etapas y disponible en informes.',
    'author': 'CosladaFon',
    'depends': ['helpdesk'],
    'data': [
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_ticket_reports.xml',
    ],
    'installable': True,
    'application': False,
}
