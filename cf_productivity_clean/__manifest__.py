
{
    'name': 'CF Productivity (Clean Base)',
    'summary': 'Módulo base limpio para informes, ranking y estadísticas (sin cron, sin vistas SQL)',
    'version': '17.0.0.1',
    'author': 'CFON / ChatGPT',
    'category': 'Productivity',
    'depends': ['base'],
    'data': [
        'security/cf_productivity_security.xml',
        'security/ir.model.access.csv',
        'views/cf_productivity_report_views.xml',
        'views/cf_productivity_ranking_views.xml',
        'views/cf_productivity_stats_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
