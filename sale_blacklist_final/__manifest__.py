{
    "name": "Sale - Blacklist / Anti Fraud",
    "version": "1.2",
    "summary": "Blacklist customers and block order/ship when matching fraud data",
    "category": "Sales",
    "author": "CFON / CosladaFon",
    "depends": ["sale_management", "stock", "contacts"],
   "data": [
    "security/ir.model.access.csv",
    "views/sale_blacklist_views.xml",
    "views/fix_blacklist_menu.xml",  # 👈 añade esta línea
],
    "installable": True,
    "application": False
}
