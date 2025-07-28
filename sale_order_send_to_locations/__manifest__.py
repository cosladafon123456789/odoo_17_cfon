{
    "name": "Sale Order Send to Locations",
    "version": "1.3",
    "depends": ["sale", "stock"],
    "author": "ChatGPT",
    "category": "Sales",
    "description": "Send products from Sale Orders to internal stock locations with optional IMEI tracking.",
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/send_to_location_wizard_view.xml"
    ],
    "installable": True,
    "application": False
}
