{
    'name': 'Sale Mini Dashboard',
    'version': '17.0',
    'category': 'Sales',
    'summary': '16 June, Mini dashboard for Sales, Displays the total amount and count'
               ' of Quotations and Sale Orders',
    'description': """This module is developed for displaying the count of 
    quotations and sale orders, total amount for sale orders and total 
    amount for quotations.""",
    'author': 'Preciseways',
    'website': 'http://www.preciseways.com',
    'depends': ['base', 'sale_management'],
    'data': ['views/sale_order_views.xml'],
    'assets': {
        'web.assets_backend': [
            'sale_mini_dashboard/static/src/xml/*.xml',
            'sale_mini_dashboard/static/src/js/*.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
