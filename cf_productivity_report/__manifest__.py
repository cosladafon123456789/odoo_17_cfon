{
    "name": "CF Productividad Report",
    "version": "1.0",
    "summary": "Registro automático de productividad (Reparaciones, Tickets y Pedidos)",
    "description": """
Registra automáticamente la productividad de todos los usuarios de Odoo:
- Reparaciones finalizadas
- Tickets respondidos
- Pedidos/entregas validados
Solo los administradores técnicos pueden ver el dashboard.
    """,
    "author": "CFON Telecomunicaciones S.L.",
    "category": "Inventory/Reporting",
    "depends": ["base", "repair", "helpdesk", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/productivity_views.xml",
        "views/menu_productivity.xml",
        "views/productivity_ticket_daily_views.xml",
        "views/repair_reason_wizard_views.xml",
        "views/productivity_stats_views.xml",
        "views/productivity_repair_stats_views.xml"
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3"
}