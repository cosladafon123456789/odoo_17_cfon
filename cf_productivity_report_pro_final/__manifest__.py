
{
    'name': 'CF Productividad Pro',
    'summary': 'Suite de productividad: informe, ranking, estadísticas y acción manual (sin cron)',
    'version': '17.0.1.0.0',
    'author': 'CFON / ChatGPT',
    'category': 'Productivity',
    'depends': ['base', 'mail'],
    'data': [
        'security/cf_productivity_security.xml',
        'security/ir.model.access.csv',
        'views/productivity_views.xml',
        'views/productivity_stats_views.xml',
        'views/productivity_ranking_views.xml',
        'views/dashboard_views.xml',
        'views/mail_template.xml',
        'data/server_actions.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
