# -*- coding: utf-8 -*-
{
    "name": "Product Lot & Serial Filter",
    "summary": """
        Products search by Lot and Serial Number
    """,
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "category": "Inventory/Inventory",
    "depends": ['stock'],
    "data": [
        'views/stock_scrap_views.xml',
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "sequence": 10,
    "author": "SPD Solutions Pvt. Ltd.",
    "maintainer": "SPD Solutions Pvt. Ltd.",
    "images": [
        "static/description/banner.png",
    ],
    "description": """
        This module allows users to search products by Lot and Serial Number in Product.
    """,
}
