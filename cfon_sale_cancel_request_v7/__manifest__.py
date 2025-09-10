{
    "name": "CFON Sale Cancel Request",
    "version": "17.0.1.0",
    "author": "CFON",
    "summary": "Solicitud de cancelación interna en órdenes de venta",
    "depends": ["sale_management", "mail", "sales_team", "web"],
    "data": [
        "security/cancel_request_groups.xml",
        "security/ir.model.access.csv",
        "views/sale_cancel_request_wizard_views.xml",
        "views/sale_order_views.xml",
    ],
    "application": False,
    "installable": True,
    "license": "OEEL-1"
}