{
    'name': 'Marketplaces Helpdesk',
    'version': '17.0.1.0.0',
    'summary': 'Gestión de mensajes y tickets de marketplaces Mirakl (MediaMarkt, Carrefour, PCComponentes, etc.)',
    'description': 'Permite recibir, gestionar y responder mensajes de clientes de marketplaces conectados a Mirakl directamente desde Odoo.',
    'category': 'Helpdesk',
    'author': 'CFON Telecomunicaciones',
    'website': 'https://www.cosladafon.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
    'views/marketplace_account_views.xml',
    'views/marketplace_ticket_views.xml',
    'views/res_config_settings_views.xml',
    'views/menu.xml',  # 👈 el tuyo se llama así, no hace falta renombrarlo
],
