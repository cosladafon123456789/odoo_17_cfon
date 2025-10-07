{
    'name': 'Marketplaces Helpdesk',
    'version': '17.0.1.0.0',
    'summary': 'Integración con Mirakl y gestión de tickets desde Odoo',
    'description': """
Permite conectar Odoo con marketplaces Mirakl (como MediaMarkt, Carrefour, PCComponentes, etc.)
y visualizar los mensajes o tickets de los clientes directamente desde Odoo.
""",
    'category': 'Helpdesk',
    'author': 'CFON Telecomunicaciones',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
