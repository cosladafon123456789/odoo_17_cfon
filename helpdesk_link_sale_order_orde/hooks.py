import re

def post_init_hook(env):
    Ticket = env['helpdesk.ticket']
    SaleOrder = env['sale.order']

    tickets = Ticket.search([('sale_order_id', '=', False)])
    for ticket in tickets:
        if ticket.name:
            match = re.search(r'(SO\d+)', ticket.name)
            if match:
                so_name = match.group(1)
                order = SaleOrder.search([('name', '=', so_name)], limit=1)
                if order:
                    ticket.sale_order_id = order.id
