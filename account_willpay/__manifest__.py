# -*- coding: utf-8 -*-
{
    'name': "Account Willpay",

    'summary': """
        Account Willpay""",

    'description': """
        
        Nanobytes - Account Willpay
        
        This module was made by Nanobytes Informatica y Telecomunicaciones S.L,
        for more information, contact us : https://nanobytes.es
        
    """,

    'author': "Nanobytes Informatica y Telecomunicaciones S.L",
    'website': "https://nanobytes.es",
    'category': 'custom',
    'version': '1.0.4',
    'depends': ['account', 'l10n_es'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_willpay_views.xml',
        'views/account_journal_views.xml',
        'wizards/account_make_willpay_views.xml',
        # 'data/account_chart_template_data.xml',
        'data/ir_sequence_data.xml'
    ],
    'qweb': [],
    'application': True,
    'license': 'OEEL-1',
    'assets': {}
}