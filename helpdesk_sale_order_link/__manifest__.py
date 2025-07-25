{
    "name": "Helpdesk Sale Order Link",
    "version": "17.0.1.0.0",
    "category": "Helpdesk",
    "summary": "Detecta número de pedido en el título del ticket y lo vincula automáticamente",
    "depends": ["helpdesk", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False,
}
