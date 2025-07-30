# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################

from . import models
from . import wizards

def pre_init_check(cr):
    from odoo.service import common
    # from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    
    if not server_serie == '17.0':
        raise Warning(
            'Module support Odoo series 17.0 found {}.'.format(server_serie))
    return True
