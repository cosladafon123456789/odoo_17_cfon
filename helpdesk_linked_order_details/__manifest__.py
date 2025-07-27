{
    "name": "Helpdesk Linked Order Details",
    "version": "17.0.1.0.0",
    "category": "Helpdesk",
    "summary": "Muestra productos y nº de serie del pedido vinculado al ticket",
    "depends": ["helpdesk", "sale", "stock", "helpdesk_sale_order_link"],
    "data": [
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
