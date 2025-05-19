# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_data_risk(self):
        parent_id = self.partner_id._get_parent_id()
        _logger.info("comprobando el padre")
        _logger.info(parent_id)
        _logger.info("tiene caucion")
        _logger.info(parent_id.risk_caution)
        _logger.info("total del pedido")
        _logger.info(self.amount_total)
        if parent_id._check_caution():
            if parent_id and parent_id.state == 'locked':
                raise ValidationError(_("You cannot confirm the order! The partner is in state 'Locked'. "))
            if parent_id._check_risk(self.amount_total):
                raise ValidationError(_("You cannot confirm the order! The partner has a total amount without paying more than the risk credit. "))
            #if parent_id._check_caution():
            #    raise ValidationError(_("You cannot confirm the order! The partner has checked 'Credit and caution'. "))
    
        return True
    
    def action_confirm(self):
        _logger.info("primero checkeamos el riesgo")
        self.check_data_risk()
        _logger.info("confirmamos")
        return super().action_confirm()
