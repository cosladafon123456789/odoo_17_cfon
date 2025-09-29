
{
    "name": "Helpdesk Tickets en Pedidos de Venta",
    "version": "1.0",
    "depends": ["sale_management", "helpdesk"],
    "author": "ChatGPT",
    "category": "Sales",
    "summary": "Muestra los tickets de Helpdesk en el pedido de venta relacionado",
    "data": [
        "views/helpdesk_ticket_view.xml",
        "views/sale_order_view.xml",
        "data/helpdesk_action.xml"
    ],
    "installable": True,
    "application": False,
}
