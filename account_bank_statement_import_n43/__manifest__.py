# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import N43 Bank Statement',
    'category': 'Accounting/Accounting',
    'version': '1.0',
    'depends': ['account', 'account_bank_statement_import'],
    'description': """
Module to import N43 bank statements.
======================================

This module allows you to import the machine readable N43 Files in Odoo: they are parsed and stored in human readable format in
Accounting \ Bank and Cash \ Bank Statements.
    """,
    'data': [
        'views/account_journal_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
