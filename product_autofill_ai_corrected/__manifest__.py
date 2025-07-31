# -*- coding: utf-8 -*-
{
    'name': 'Product Autofill with AI',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Rellena automáticamente los campos de productos con IA (OpenAI)',
    'description': 'Al escribir el nombre del producto, se rellena automáticamente marca, modelo, RAM, almacenamiento, etc. usando OpenAI',
    'author': 'CosladaFon + ChatGPT',
    'depends': ['base', 'product'],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
