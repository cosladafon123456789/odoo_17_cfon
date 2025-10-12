
{
    "name": "Informe de Reparaciones (MIN)",
    "version": "17.0.0.1",
    "summary": "Wizard al finalizar reparación con motivo y registro por técnico (mínimo y robusto)",
    "author": "CFON Telecomunicaciones",
    "license": "LGPL-3",
    "depends": ["repair"],
    "data": [
        "views/repair_order_inherit_views.xml",
        "views/repair_reason_wizard_views.xml",
        "views/report_action.xml",
        "views/menus.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False
}
