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
    "category": "Productivity",
    "depends": ["base", "repair", "helpdesk", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/productivity_views.xml",
        "views/menu_productivity.xml",
        "views/repair_reason_wizard_views.xml"
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3"
}