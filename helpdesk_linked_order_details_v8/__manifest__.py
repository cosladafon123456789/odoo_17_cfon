{
    "name": "Helpdesk Linked Order Details V8",
    "version": "17.0.1.0.8",
    "category": "Helpdesk",
    "summary": "Tabla limpia debajo de Pedido de Origen con solo Fecha de Compra, Producto y Nº Serie",
    "depends": ["helpdesk", "sale", "stock", "helpdesk_sale_order_link"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
