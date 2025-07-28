{
    "name": "Helpdesk Linked Order Details V2",
    "version": "17.0.1.0.2",
    "category": "Helpdesk",
    "summary": "Muestra productos y nº de serie del pedido vinculado al ticket (modelo persistente)",
    "depends": ["helpdesk", "sale", "stock", "helpdesk_sale_order_link"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
