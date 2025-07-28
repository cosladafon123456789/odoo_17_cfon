{ 
    'name': 'Send Sale Order to Location',
    'version': '1.0',
    'depends': ['sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'wizards/send_to_location_wizard_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
