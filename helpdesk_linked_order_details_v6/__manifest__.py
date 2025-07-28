{
    "name": "Helpdesk Linked Order Details V6",
    "version": "17.0.1.0.6",
    "category": "Helpdesk",
    "summary": "Corrige visualización: tabla completa justo debajo del pedido de origen",
    "depends": ["helpdesk", "sale", "stock", "helpdesk_sale_order_link"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
