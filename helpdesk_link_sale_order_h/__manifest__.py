{
    "name": "Helpdesk Link Sale Order",
    "version": "17.0.1.0.1",
    "depends": ["helpdesk", "sale_management"],
    "category": "Helpdesk",
    "summary": "Asocia automáticamente pedidos de venta con tickets de Helpdesk y muestra los tickets en el pedido.",
    "author": "CosladaFon / ChatGPT",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "data": [
        "views/helpdesk_ticket_view.xml",
        "views/sale_order_view.xml"
    ],
    "post_init_hook": "post_init_hook"
}
