{
    "name": "Helpdesk Link Sale Order",
    "version": "17.0.1.0.0",
    "depends": ["helpdesk", "sale_management"],
    "category": "Helpdesk",
    "summary": "Auto-link sale order to helpdesk ticket based on title",
    "author": "TuNombre",
    "installable": True,
    "application": False,
    "data": [
        "views/helpdesk_ticket_view.xml",
        "views/sale_order_view.xml"
    ],,
    "post_init_hook": "post_init_hook"
}