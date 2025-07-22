# -*- coding: utf-8 -*-
{
    'name': "Vendor Evaluation Management",
    'summary': """ Create Vendor Rating Evaluation Using Different Questions.

        Manager Can Create Different Questions and Questions Template for Vendor Evaluations.

        Configuration for Sales Users and Sales Manager.

        User/Manager Can Evaluate Rating On Confirm/Done Button and Refresh Link.

        Evaluation Rating and Date are Presented in Different Views, such as Forms, Lists, and Kanban of Vendors.

        Evaluation Rating is Presented in Views of Purchase Order.

        Print Evaluation PDF Report.

        Send Evaluation to Vendor.

        Send Email With Attachment.
    """,

    'description': "Vendor Evaluation.",
    'author' : 'Preciseways',
    'website': "http://www.preciseways.com",
    'category': 'Purchases',
    'version': '17.0',
    'depends': ['purchase'],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/vendor_evaluation_views.xml',
        'views/vendor_evaluation_question_views.xml',
        'views/inherit_partner_views.xml',
    ],
    
    'installable': True,
    'application': True,
    'price': 21.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images':['static/description/banner.png'],

}
