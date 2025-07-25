{
    "name": "Helpdesk Sale Order x_studio_origen Tag (Final)",
    "version": "17.0.1.0.4",
    "category": "Helpdesk",
    "summary": "Asigna una etiqueta al ticket basada en el campo x_studio_origen del pedido sin duplicar campos",
    "depends": ["helpdesk", "sale", "helpdesk_sale_order_link"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
