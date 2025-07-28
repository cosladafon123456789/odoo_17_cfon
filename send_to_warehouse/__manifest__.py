{
    "name": "Send to Warehouse from Sale Order",
    "version": "1.0",
    "depends": ["sale", "stock"],
    "author": "ChatGPT",
    "category": "Sales",
    "description": "Adds a button to send products from a sale order to a selected warehouse.",
    "data": [
        "views/sale_order_view.xml",
        "wizard/send_to_warehouse_wizard_view.xml"
    ],
    "installable": True,
    "application": False
}