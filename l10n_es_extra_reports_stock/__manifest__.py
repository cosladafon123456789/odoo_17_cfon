# -*- coding: utf-8 -*-
{
    'name': 'Spain - Accounting Extra Stock Reports',
    'version': '16.0.1',
    'author': 'Nanobytes Informatica y Telecomunicaciones S.L',
    'website': 'https://nanobytes.es',
    'category': 'Accounting',
    'description': """
        Accounting stock reports for Spain
    """,
    'depends': [
        'account', 'l10n_es', 'l10n_es_reports', 'account_accountant', 'product', 'stock', 'l10n_es_extra_reports',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/plastic_models_views.xml',
        'views/stock_picking_views.xml',
        'data/plastic_models_data.xml',
        'data/book_es_plastic_stock_report.xml',
        'views/aeat_menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OEEL-1',
}
