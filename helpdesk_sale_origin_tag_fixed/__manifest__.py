{
    "name": "Helpdesk Sale Order Origin Tag",
    "version": "17.0.1.0.1",
    "category": "Helpdesk",
    "summary": "Agrega una etiqueta al ticket con el valor del campo origen del pedido asociado",
    "depends": ["helpdesk", "sale", "helpdesk_sale_order_link"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
