
# -*- coding: utf-8 -*-
from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    cf_whatsapp_tecomprotumovil_sent = fields.Boolean(
        string="WhatsApp TeComproTuMovil ya enviado",
        help="Si está marcado, no se volverá a enviar automáticamente el WhatsApp de la plantilla 'tecomprotumovil' para este contacto."
    )
