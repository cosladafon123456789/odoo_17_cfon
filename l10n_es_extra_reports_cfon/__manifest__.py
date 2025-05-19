# -*- coding: utf-8 -*-
{
    'name': 'Spain - Accounting Extra Reports Cfon',
    'version': '17.0.0.1',
    'author': 'Nanobytes Informatica y Telecomunicaciones S.L',
    'website': 'https://nanobytes.es',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
        Accounting reports for Spain
    """,
    'depends': [
        'l10n_es_extra_reports', 'perso_cfon'
    ],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OEEL-1',
}
