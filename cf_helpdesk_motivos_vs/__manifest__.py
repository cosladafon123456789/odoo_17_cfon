{
    'name': 'CF Helpdesk Motivos',
    'version': '17.0.4.0',
    'summary': 'Gestión de motivos de devolución en Helpdesk',
    'description': 'Campo motivo de devolución obligatorio en etapas clave y disponible en informes con menú independiente.',
    'author': 'CosladaFon',
    'depends': ['helpdesk'],
    'data': [
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_ticket_reports.xml',
    ],
    'installable': True,
    'application': False,
}
