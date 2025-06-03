# -*- coding: utf-8 -*-
{
    "name" : "Sale Service Management - May 31, 2025",
    "version" : "17.0",
    "category" : "Sales",
    'summary': """Repair management typically includes the following key activities:
                create repair for selected products and process repair order (add/remove components and create invoice)
                once all repair orders are finished than main product will be delivered to customer
                Repair Management
                Sale repair Management
                Sale service management
                Work Order Management
                Resource Allocation
                Maintenance Scheduling
                Joborder Management
                Jobcard Management
                Maintenance Management
    """,
    'website': "http://www.preciseways.com",
    'author': "Preciseways",
    "depends" : ['sale_management', 'repair', 'sale_stock', 'purchase', 'product_expiry'],
    'data': [
            # "data/cron.xml",
            "security/ir.model.access.csv",
            "wizard/repair_order_wizard_views.xml",
            "wizard/replace.xml",
            "wizard/all_action_wizard.xml",
            "wizard/lot_quantity_wizard.xml",
            "views/purchase_order.xml",
            "views/sale_order_inherit_views.xml",
            "views/stock_picking.xml",
            ],
    
    "application": True,
    "installable": True,
    'images': ['static/description/banner.png'],
    'price': 19,
    'currency': 'EUR',
    'license': 'OPL-1',
}

