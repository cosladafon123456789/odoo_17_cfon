# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from . import models
from . import controllers

from odoo.addons.payment import setup_provider, reset_payment_provider

def pre_init_check(cr):
    from odoo.service import common
    # from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if not 16.0 < float(server_serie) <= 17.0:raise Warning('Module support Odoo series 17.0 found {}.'.format(server_serie))
    return True

def post_init_hook(env):
    setup_provider(env, 'paypal_express')


def uninstall_hook(env):
    reset_payment_provider(env, 'paypal_express')
