{
    'name': 'CF Productividad Pro',
    'summary': 'Suite avanzada de productividad: intervalos, ranking, pausas, dashboard y KPIs',
    'version': '17.0.1.0.0',
    'author': 'CFON / ChatGPT',
    'category': 'Productivity',
    'depends': ['base', 'mail'],
    'data': [
        'security/cf_productivity_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/server_actions.xml',
        'views/productivity_views.xml',
        'views/productivity_stats_views.xml',
        'views/productivity_ranking_views.xml',
        'views/dashboard_views.xml',
        'views/mail_template.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
