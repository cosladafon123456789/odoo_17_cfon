{
    "name": "Helpdesk Linked Order Details V12",
    "version": "17.0.1.0.12",
    "category": "Helpdesk",
    "summary": "Vista kanban corregida para mostrar producto, serie y fecha correctamente",
    "depends": ["helpdesk", "sale", "stock", "helpdesk_sale_order_link"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml"
    ],
    "installable": True,
    "application": False
}
