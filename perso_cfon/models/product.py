# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #GAP V1
    is_rebu = fields.Boolean(string=_("Is REBU"), default=False)
    rebu_tax_id = fields.Many2one("account.tax", string=_("REBU Tax"))