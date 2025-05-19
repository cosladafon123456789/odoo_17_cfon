# -*- coding: utf-8 -*-
{
    'name': "Partner Risk",

    'summary': """
        Manage your partner risk""",

    'description': """
        
        Nanobytes - Partner Risk
        
        This module was made by Nanobytes Informatica y Telecomunicaciones S.L,
        for more information, contact us : http://nanobytes.es
        
    """,

    'author': "Nanobytes Informatica y Telecomunicaciones S.L",
    'category': 'Partner',
    'version': '1.1',
    'depends': ['base', 'sale', 'contacts', 'sale_management'],
    'installable': True,
    'application': False,
    'license': 'OEEL-1',
    'data': [
        'security/ir.model.access.csv',
        'views/res_views.xml',
        'security/security.xml'
    ],
}
