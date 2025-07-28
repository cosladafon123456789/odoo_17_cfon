{
    "name": "Helpdesk Linked Order Details V5",
    "version": "17.0.1.0.5",
    "category": "Helpdesk",
    "summary": "Corrige el campo computado para mostrar productos y números de serie del pedido vinculado",
    "depends": ["helpdesk", "sale", "stock", "helpdesk_sale_order_link"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
