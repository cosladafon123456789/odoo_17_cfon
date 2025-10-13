
{
    "name": "Productividad CF Pro v3 (bloques + email diario + etapas Helpdesk + métrica entre pedidos)",
    "summary": "KPI con tiempo efectivo por bloques, email diario 20:00, contabiliza cambios de etapa en Helpdesk y calcula media entre validaciones de pedidos con tiempo de reseteo configurable.",
    "version": "17.0.4.0.0",
    "author": "CosladaFon",
    "category": "Productivity",
    "depends": ["base", "mail", "repair", "helpdesk", "stock", "base_setup"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/productivity_views.xml",
        "views/menu_productivity.xml",
        "views/company_productivity_views.xml",
        "views/repair_reason_wizard_views.xml",
        "views/goal_views.xml",
        "data/cron.xml"
    ],
    "application": true,
    "installable": true,
    "license": "LGPL-3"
}
