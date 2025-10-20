
{
    'name': 'CF Productividad Pro (FixedTable)',
    'summary': 'Versión sin cron y con reparación automática de la vista cf_productivity_stats',
    'version': '17.0.2.0.0',
    'author': 'CFON / ChatGPT',
    'category': 'Productivity',
    'depends': ['base'],
    'data': [
        'security/cf_productivity_security.xml',
        'security/ir.model.access.csv',
        'views/productivity_views.xml',
        'data/server_actions.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
