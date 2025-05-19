# -*- coding: utf-8 -*-
{
    'name': "Account Closing",

    'summary': """
        Account opening and closing""",
    'description': """
        
        Nanobytes - Account Closing
        
        This module was made with the intention to manage
        your account opening and closing
        
        This module was made by Nanobytes Informatica y Telecomunicaciones S.L,
        for more information, contact us : https://nanobytes.es
        
    """,
    'author': "Nanobytes Informatica y Telecomunicaciones S.L.",
    'website': "https://nanobytes.es",

    'category': 'Uncategorized',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/account_closing_wizard_view.xml',
    ],
    'license': 'LGPL-3',
}
