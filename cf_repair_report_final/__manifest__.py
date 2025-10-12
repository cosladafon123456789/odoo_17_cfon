
{
    "name": "Informe de Reparaciones",
    "version": "17.0.1.0.3",
    "summary": "Wizard al finalizar reparación para registrar motivo y generar informe diario por técnico",
    "author": "CFON Telecomunicaciones",
    "license": "LGPL-3",
    "depends": ["repair"],
    "data": [
        "views/repair_order_inherit_views.xml",
        "views/repair_reason_wizard_views.xml",
        "views/repair_report_views.xml",
        "views/repair_report_action.xml",
        "views/menus.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False
}
