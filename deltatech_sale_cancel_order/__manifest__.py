# ©  2008-2021 Deltatech
# See README.rst file on addons root folder for license details
{
    "name": "Terrabit Sale Cancel Order",
    "summary": "Cancel sales order from portal",
    "version": "17.0.0.1.1",
    "author": "Terrabit, Dan Stoica",
    "website": "https://www.terrabit.ro",
    "support": "odoo@terrabit.ro",
    "category": "Sales/Sales",
    "depends": ["sale", "portal"],
    "data": [
        "views/sale_order.xml",
        "views/stock_picking.xml",
        "views/templates.xml",
        "data/mail_template_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "price": 100.00,
    "currency": "EUR",
    "license": "OPL-1",
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "maintainers": ["danila12"],
}
