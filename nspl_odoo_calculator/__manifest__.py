# -*- coding: utf-8 -*-
{
    'name': 'Odoo Calculator',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Perform basic math calculations effortlessly within Odoo.',
    'description': """
This module adds a simple yet powerful calculator inside Odoo's backend interface.

Key Features:
✔ Perform basic arithmetic operations  
✔ Fully integrated in Odoo backend UI  
✔ Lightweight and easy to use  
✔ Built with custom JS, XML, and CSS assets
""",
    'author': 'Namah Softech Private Limited',
    'maintainer': 'Namah Softech Private Limited',
    'company': 'Namah Softech Private Limited',
    'website': 'https://www.namahsoftech.com/',
    'support': 'support@namahsoftech.com',
    'contributors': ['Vipul Sah'],
    'price': 9.99,
    'currency': 'USD',
    'depends': ['base'],
    'assets': {
        'web.assets_backend': [
            'nspl_odoo_calculator/static/src/css/calculator.css',
            'nspl_odoo_calculator/static/src/xml/calculator.xml',
            'nspl_odoo_calculator/static/src/js/calculator.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/img/banner.png'],
}
