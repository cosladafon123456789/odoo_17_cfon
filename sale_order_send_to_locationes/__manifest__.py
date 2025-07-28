{
    "name": "Send Sale Order to Inventory Locations",
    "version": "1.0",
    "depends": ["sale", "stock"],
    "category": "Sales",
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/send_to_location_wizard_view.xml"
    ],
    "installable": True,
    "application": False
}
