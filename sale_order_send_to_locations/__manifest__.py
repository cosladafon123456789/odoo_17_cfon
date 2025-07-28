{
    "name": "Sale Order Dynamic Send to Location",
    "version": "1.2",
    "depends": ["sale", "stock"],
    "author": "ChatGPT",
    "category": "Sales",
    "description": "Adds a wizard to choose the destination inventory location from a sale order.",
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/send_to_location_wizard_view.xml"
    ],
    "installable": True,
    "application": False
}
