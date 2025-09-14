
# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

CORE_MODULES = set([
    'web','base','website','mail','sale','stock','purchase','account','hr','crm','point_of_sale'
])

ASSET_TNAMES = (
    'web.assets_backend',
    'web.assets_frontend',
    'web.assets_common',
    'website.assets_frontend',
    'website.assets_editor',
    'website.assets_wysiwyg',
)

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env['ir.ui.view']
    # Find inherited QWeb templates that target any of the asset templates
    inherited_assets = View.search([
        ('type', '=', 'qweb'),
        ('inherit_id.key', 'in', ASSET_TNAMES),
        ('active', '=', True),
    ])
    to_disable = env['ir.ui.view']
    for v in inherited_assets:
        module = v._module or (v.xml_id.split('.')[0] if v.xml_id and '.' in v.xml_id else '')
        if module not in CORE_MODULES:
            to_disable |= v
    if to_disable:
        to_disable.write({'active': False})
