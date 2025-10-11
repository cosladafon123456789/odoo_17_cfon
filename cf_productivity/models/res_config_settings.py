from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


def _ids_to_param(ids):
    """Convierte lista de IDs a string separado por comas"""
    return ",".join(str(int(i)) for i in ids) if ids else ""


def _param_to_ids(param):
    """Convierte string de IDs separados por comas a lista"""
    if not param:
        return []
    try:
        return [int(x) for x in param.split(",") if x]
    except Exception as e:
        _logger.error("Error al convertir parámetros a IDs: %s", e)
        return []


PARAM_PICKING_USERS = "cf_productivity.picking_user_ids"
PARAM_REPAIR_USERS = "cf_productivity.repair_user_ids"
PARAM_HELPDESK_USERS = "cf_productivity.helpdesk_user_ids"
PARAM_SEND_DAILY = "cf_productivity.send_daily_summary"
PARAM_RECIPIENT_IDS = "cf_productivity.summary_recipient_ids"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    picking_user_ids = fields.Many2many(
        "res.users",
        "rel_cf_productivity_picking_users",
        string="Usuarios de pedidos a contabilizar",
    )
    repair_user_ids = fields.Many2many(
        "res.users",
        "rel_cf_productivity_repair_users",
        string="Usuarios técnicos a contabilizar",
    )
    helpdesk_user_ids = fields.Many2many(
        "res.users",
        "rel_cf_productivity_helpdesk_users",
        string="Usuarios de postventa a contabilizar",
    )
    send_daily_summary = fields.Boolean("Enviar resumen diario por email", default=True)
    summary_recipient_ids = fields.Many2many(
        "res.users",
        "rel_cf_productivity_summary_recipients",
        string="Destinatarios del resumen diario",
    )

    # ============================================================
    #  CARGAR VALORES DESDE ir.config_parameter
    # ============================================================
    @api.model
    def get_values(self):
        _logger.info("🟢 Cargando valores de configuración de Productividad...")
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()

        res.update(
            picking_user_ids=[(6, 0, _param_to_ids(icp.get_param(PARAM_PICKING_USERS)))],
            repair_user_ids=[(6, 0, _param_to_ids(icp.get_param(PARAM_REPAIR_USERS)))],
            helpdesk_user_ids=[(6, 0, _param_to_ids(icp.get_param(PARAM_HELPDESK_USERS)))],
            send_daily_summary=True
            if icp.get_param(PARAM_SEND_DAILY, "1") in ("1", "True", "true")
            else False,
            summary_recipient_ids=[
                (6, 0, _param_to_ids(icp.get_param(PARAM_RECIPIENT_IDS)))
            ],
        )
        _logger.info("🟢 Valores cargados correctamente: %s", res)
        return res

    # ============================================================
    #  GUARDAR VALORES EN ir.config_parameter
    # ============================================================
    def set_values(self):
        _logger.info("🔵 Guardando configuración de Productividad...")
        super().set_values()
        icp = self.env["ir.config_parameter"].sudo()
        try:
            icp.set_param(PARAM_PICKING_USERS, _ids_to_param(self.picking_user_ids.ids))
            icp.set_param(PARAM_REPAIR_USERS, _ids_to_param(self.repair_user_ids.ids))
            icp.set_param(PARAM_HELPDESK_USERS, _ids_to_param(self.helpdesk_user_ids.ids))
            icp.set_param(PARAM_SEND_DAILY, "1" if self.send_daily_summary else "0")
            icp.set_param(
                PARAM_RECIPIENT_IDS, _ids_to_param(self.summary_recipient_ids.ids)
            )
            _logger.info("✅ Configuración de productividad guardada con éxito.")
        except Exception as e:
            _logger.error("❌ Error al guardar configuración: %s", e)
