{
    "name": "Sale - Blacklist / Anti Fraud",
    "version": "1.3",
    "summary": "Bloqueo de pedidos fraudulentos según reglas personalizadas (CP, ciudad, teléfono, email, etc.)",
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
