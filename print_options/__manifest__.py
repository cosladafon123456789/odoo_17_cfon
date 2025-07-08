# -*- coding: utf-8 -*-
{
    'name': 'Printing options',
    'version': '17.0.1.0.0',
    'summary': """Opens a modal window offering options to print, download, or view PDF reports.""",
    'description': """
       Select one of the following options to handle the Printing options:

            Print: Print the PDF report directly using your browser.
            Download: Save the PDF report to your computer.
            Open: View the PDF report in a new tab.
        You can also set a default option for each report.
    """,
    'author': "Namah Softech Pvt Ltd",
    'maintainer': 'Namah Softech Pvt Ltd',
    'website': "https://namahsoftech.com/",
    'category': 'Productivity',
    'depends': ['web'],
    'images': ['static/description/banner.gif'],
    'data': [
        'views/ir_actions_printing_options.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'print_options/static/src/js/PrintOptionsModal.js',
            'print_options/static/src/js/qweb_action.js',
            'print_options/static/src/**/*.xml'
        ]
    },
    'application': True,
}
