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
    "name"                  :  "Payment Refund Base",
    "summary"               :  """Module provides refund base features.""",
    "category"              :  "Payment",
    "version"               :  "1.0.1",
    "author"                :  "Webkul Software Pvt. Ltd.",
    "license"               :  "Other proprietary",
    "website"               :  "https://store.webkul.com/",
    "description"           :  """
                                This module provides the foundational infrastructure for a refund-based payment flow in Odoo.
                                Instead of processing direct payments,all transactions are initiated and managed as refunds.
                                It introduces a generic wizard that captures common details required for processing refunds, regardless of the specific payment provider.
                                This shared interface ensures consistency across different refund implementations and simplifies the development of provider-specific refund modules.
                                This base module is designed to be extended by additional modules that implement the actual refund logic for various payment providers.
                               """,
    "live_test_url"         :  "http://odoodemo.webkul.com/?module=wk_payment_refund_base&version=17.0",
    "depends"               :  ['account'],
    "data"                  :  [    
                                    'security/ir.model.access.csv',
                                    'views/payment_transaction_view.xml',
                                    'wizards/move_refund.xml',
                                ],
    "images"                :  ["static/description/banner.png"],
    "application"           :  True,
    "installable"           :  True,
    "price"                 :  9,
    "currency"              :  "USD",
    "pre_init_hook"         :  "pre_init_check",
}
