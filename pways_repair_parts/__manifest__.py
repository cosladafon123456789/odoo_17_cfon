{
	'name': 'Pways Repair Parts & RMA Extension',
	'version': '17.0',
	'category': 'Sales',
	"summary": """Auto-purchase missing repair parts and start RMA from serial numbers.""",
	"description": """Triggers purchase requests for out-of-stock parts in repairs and adds RMA/repair button to serial number view.""",
	'author': 'Preciseways',
	'website': 'http://www.preciseways.com',
	'depends': ['repair', 'purchase', 'stock', 'pways_sale_repair_management'],
	'data': [
            "security/ir.model.access.csv",
            "views/stock_move.xml",
			"views/stock_lot.xml",
			"wizard/repair_order_wizard_views.xml",
            ],
	'installable': True,
	'application': True,
	'license': 'OPL-1',
	'currency': 'EUR'
}
