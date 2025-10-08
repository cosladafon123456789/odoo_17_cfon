{
    "name": "Sale - Blacklist / Anti Fraud (Validate Only)",
    "version": "1.4",
    "summary": "Bloqueo de entregas si el cliente coincide con lista negra (sin bloquear pedidos)",
    "category": "Sales",
    "author": "CFON Telecomunicaciones / CosladaFon",
    "depends": ["sale_management", "stock", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_blacklist_views.xml",
        "views/fix_blacklist_menu.xml"
    ],
    "installable": True,
    "application": True
}
