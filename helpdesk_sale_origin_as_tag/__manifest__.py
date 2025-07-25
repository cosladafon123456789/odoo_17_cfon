{
    "name": "Helpdesk Sale Order x_studio_origen as Tag",
    "version": "17.0.1.0.3",
    "category": "Helpdesk",
    "summary": "Asigna automáticamente una etiqueta al ticket basada en el campo x_studio_origen del pedido vinculado",
    "depends": ["helpdesk", "sale", "helpdesk_sale_order_link"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
