# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Paypal Express Checkout Payment Acquirer",
  "summary"              :  """Odoo Paypal Express Checkout Payment Acquirer integrates Paypal with your Odoo for accepting quick payments from customers.""",
  "category"             :  "eCommerce",
  "version"              :  "1.2.2",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-website-paypal-express-checkout-payment-acquirer.html",
  "description"          :  """Paypal Express Checkout Payment Acquirer
Odoo Paypal Express Checkout Payment Acquirer
Paypal Express Checkout Payment Acquirer in Odoo
Paypal Integration
Odoo Paypal Express
Paypal Express
Paypal Express Checkout
Paypal Express Checkout Integration
Configure Paypal
PayPal integration with Odoo
Paypal Express Checkout Payment integration with Odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_paypal_express&custom_url=/shop",
  "depends"              :  ['website_sale','payment'],
  "data"                 :  [
                             'views/template.xml',
                             'views/paypal_checkout_template.xml',
                             'views/payment_provider_views.xml',
                             'data/payment_provider_data.xml',
                            ],
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "assets"               :  {
    "web.assets_frontend":  [
        "payment_paypal_express/static/src/js/express_checkout.js",
        "payment_paypal_express/static/src/css/express_checkout.css",
    ]
  },
  "price"                :  149,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "post_init_hook"       :  "post_init_hook",
  "uninstall_hook"       :  "uninstall_hook",
}
