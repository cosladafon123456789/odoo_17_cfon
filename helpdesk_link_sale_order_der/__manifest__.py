{
    "name": "Helpdesk Link Sale Order",
    "version": "17.0.1.0.2",
    "depends": ["helpdesk", "sale_management"],
    "category": "Helpdesk",
    "summary": "Muestra los tickets vinculados al pedido mediante linked_sale_order_id",
    "author": "CosladaFon / ChatGPT",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "data": [
        "views/helpdesk_ticket_view.xml",
        "views/sale_order_view.xml"
    ]
}
