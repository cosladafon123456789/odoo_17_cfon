# -*- coding: utf-8 -*-
{
    'name': 'CF WhatsApp on Purchase Deliveries',
    'summary': "Envía automáticamente la plantilla de WhatsApp 'tecomprotumovil' al validar entregas de compras marcadas y evita reenvíos al mismo cliente.",
    'version': '17.0.1.0.0',
    'author': 'CosladaFon + ChatGPT',
    'category': 'Tools',
    'license': 'OPL-1',
    'depends': ['stock', 'purchase', 'whatsapp'],
    'data': [
        'data/ir_config_parameter.xml',
        'data/ir_cron_dummy.xml'
    ],
    'installable': True,
    'application': False,
}
