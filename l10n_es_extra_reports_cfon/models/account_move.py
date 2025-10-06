# -*- coding: utf-8 -*-

from datetime import datetime, date
from odoo import fields, models, api, _, exceptions

from odoo.exceptions import UserError, ValidationError

# Import logging
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_particular = fields.Boolean(string=_("Is particular"), default=False)

    @api.depends('partner_id.country_id', 'commercial_partner_id.is_company', 'is_rebu')
    def _compute_l10n_es_reports_mod349_available(self):
        super(AccountMove, self)._compute_l10n_es_reports_mod349_available()
        for record in self:
            if record.is_rebu:
                record.l10n_es_reports_mod349_available = False

    @api.depends('invoice_line_ids')
    def _is_sii_available(self):
        super(AccountMove, self)._is_sii_available()
        for invoice in self:
            is_sii_available = False
            if invoice.is_rebu:
                invoice.is_sii_available = True

    def _check_auto_identify(self):
        super(AccountMove, self)._check_auto_identify()
        reg_key_obj = self.env['sii.reg.key']
        for r in self:
            if r.is_auto_identify:

                if r.is_rebu:
                    sii_reg_key_id = reg_key_obj.search([('code', '=', '03'), ('type', '=', 'sale')], limit=1)
                    if sii_reg_key_id:
                        r.sii_reg_key_id = sii_reg_key_id.id

                    if r.is_particular:
                        sii_invoice_type_id = self.env['sii.invoice.type'].search([('code', '=', 'F6')], limit=1).id
                        if sii_invoice_type_id:
                            r.sii_invoice_type_id = sii_invoice_type_id

    def _get_sii_out_taxes(self, sii_map):
        if self.is_rebu:
            taxes_sii = {
                "DesgloseFactura": {
                    "Sujeta": {
                        "NoExenta": {
                            "TipoNoExenta": "S1",
                            "DesgloseIVA": {
                                "DetalleIVA": [{
                                    "BaseImponible": 0,
                                }]
                            }
                        }
                    }
                }
            }
            return taxes_sii
        else:
            return super(AccountMove, self)._get_sii_out_taxes(sii_map)
        

    def _get_sii_in_taxes(self, sii_map):
        _logger.info(" ")
        _logger.info(" INICIAR _get_sii_in_taxes_____________________________________________")
        if self.is_rebu:
            taxes_sii = {
                'DesgloseIVA': {
                    'DetalleIVA': [
                        {
                            'TipoImpositivo': 0, 
                            'BaseImponible': 0, 
                            'CuotaSoportada': 0
                        }
                    ]
                }
            }
            return taxes_sii
        else:
            return super(AccountMove, self)._get_sii_in_taxes(sii_map)