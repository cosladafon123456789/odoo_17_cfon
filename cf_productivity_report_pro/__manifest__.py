{
    "name": "Productividad CF Pro",
    "summary": "KPI, objetivos, ranking, filtros rápidos (Hoy/Semana/Mes) y control de acceso",
    "version": "17.0.2.0.0",
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
        "views/goal_views.xml"
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3"
}
