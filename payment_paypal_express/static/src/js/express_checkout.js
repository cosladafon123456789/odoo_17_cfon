/** @odoo-module **/

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
// import PaymentForm from "@payment/js/checkout_form";
import paymentForm from '@payment/js/payment_form';
// import core from "@web/legacy/js/services/core";
import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import "@website_sale/js/website_sale_delivery";

publicWidget.registry.websiteSaleDelivery.include({
    _disablePayButton: function () {
        this._super.apply(this, arguments);
        $('#paypal-button').hide()
    },
    _handleCarrierUpdateResultBadge: function (result) {
        if ($("input[name='delivery_type']:checked").length) {
            var carrier_id = parseInt($("input[name='delivery_type']:checked").val())
            var payment_method = $("input[name='o_payment_radio']:checked")
            if (result.carrier_id == carrier_id && !result.status) {
                $('#paypal-button').hide()
            }
            else if (payment_method.length && payment_method.data('provider-code') == 'paypal_express') {
                $('#paypal-button').show()
            }
        }
        this._super.apply(this, arguments);

    }
})

function get_payer_data(data_values) {
    var payer = {}
    if (!data_values) {
        return payer
    }
    if (!data_values.billing_country_code || !data_values.billing_zip_code || !data_values.billing_area2) {
        return payer
    }
    if (data_values.billing_first_name || data_values.billing_last_name) {
        var name = {}
        if (data_values.billing_first_name) {
            name['given_name'] = data_values.billing_first_name
        }
        if (data_values.billing_last_name) {
            name['surname'] = data_values.billing_last_name
        }
        payer['name'] = name
    }
    var address = {}
    if (data_values.billing_address_l1) {
        address['address_line_1'] = data_values.billing_address_l1
    }
    if (data_values.billing_area2) {
        address['admin_area_2'] = data_values.billing_area2
    }
    if (data_values.billing_area1) {
        address['admin_area_1'] = data_values.billing_area1
    }
    if (data_values.billing_zip_code) {
        address['postal_code'] = data_values.billing_zip_code
    }
    if (data_values.billing_country_code) {
        address['country_code'] = data_values.billing_country_code
    }
    payer['address'] = address
    if (data_values.billing_email) {
        payer['email_address'] = data_values.billing_email
    }
    if (data_values.billing_phone.match('^[0-9]{1,14}?$')) {
        payer['phone'] = {
            phone_type: "MOBILE",
            phone_number: {
                national_number: data_values.billing_phone,
            }
        }
    }
    return payer
}
function get_shipping_data(data_values) {
    var shipping = {}
    if (!data_values) {
        return shipping
    }
    if (!data_values.shipping_country_code || !data_values.shipping_zip_code || !data_values.shipping_area2) {
        return shipping
    }
    if (data_values.shipping_partner_name) {
        shipping['name'] = {
            full_name: data_values.shipping_partner_name,
        }
    }
    var shipping_address = {}
    if (data_values.shipping_address_l1) {
        shipping_address['address_line_1'] = data_values.shipping_address_l1
    }
    if (data_values.shipping_area2) {
        shipping_address['admin_area_2'] = data_values.shipping_area2
    }
    if (data_values.shipping_area1) {
        shipping_address['admin_area_1'] = data_values.shipping_area1
    }
    if (data_values.shipping_zip_code) {
        shipping_address['postal_code'] = data_values.shipping_zip_code
    }
    if (data_values.shipping_country_code) {
        shipping_address['country_code'] = data_values.shipping_country_code
    }
    shipping['address'] = shipping_address
    return shipping
}



paymentForm.include({
    willStart: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            return jsonrpc('/paypal/express/checkout/url').then(function (url) {
                if (url) {
                    return loadJS(url).then(function () {
                        if (self.$el.length > 0 && $(self.$el[0]).hasClass('o_payment_form')) {
                            self.checkout_override();
                        }
                    });
                }
            });
        });
    },

    get_btn_style: function () {
        return {
            size: 'small',
            color: 'gold',
            shape: 'pill',
            label: 'pay',
        }
    },

    order_values: async function () {
        var self = this;
        var form = $('.o_payment_form')
        var checked_radio = form.find('input[type="radio"]:checked');
        if (checked_radio.length !== 1) {
            return;
        }
        checked_radio = checked_radio[0];
        var provider = checked_radio.dataset.providerCode;
        if (provider === 'paypal_express') {
            var values = self.paymentContext;
            values.tokenizationRequested = false;
            values.is_validation = false;
            values.providerId = $(checked_radio).data("providerId")
            values.paymentMethodId = $(checked_radio).data("paymentOptionId")
            values.tokenId = Number($(checked_radio).data['paymentOptionId'])
            return jsonrpc(self.paymentContext.transactionRoute, this._prepareTransactionRouteParams('paypal_express', $(checked_radio).data("payment-option-id"), 'redirect')).then(function (result) {
                var newform = document.createElement('div');
                var $newform = $(newform)
                $newform.append(result["redirect_form_html"]);
                return {
                    amount: parseFloat($newform.find('input[name="amount"]').val()).toFixed(2),
                    reference: $newform.find('input[name="invoice_num"]').val(),
                    so_reference: $newform.find('input[name="so_reference"]').val(),
                    currency_code: $newform.find('input[name="currency_code"]').val(),
                    billing_first_name: $newform.find('input[name="billing_first_name"]').val(),
                    billing_last_name: $newform.find('input[name="billing_last_name"]').val(),
                    billing_phone: $newform.find('input[name="billing_phone"]').val(),
                    billing_email: $newform.find('input[name="billing_email"]').val(),
                    billing_address_l1: $newform.find('input[name="billing_address_l1"]').val(),
                    billing_area1: $newform.find('input[name="billing_area1"]').val(),
                    billing_area2: $newform.find('input[name="billing_area2"]').val(),
                    billing_zip_code: $newform.find('input[name="billing_zip_code"]').val(),
                    billing_country_code: $newform.find('input[name="billing_country_code"]').val(),
                    shipping_partner_name: $newform.find('input[name="shipping_partner_name"]').val(),
                    shipping_address_l1: $newform.find('input[name="shipping_address_l1"]').val(),
                    shipping_area1: $newform.find('input[name="shipping_area1"]').val(),
                    shipping_area2: $newform.find('input[name="shipping_area2"]').val(),
                    shipping_zip_code: $newform.find('input[name="shipping_zip_code"]').val(),
                    shipping_country_code: $newform.find('input[name="shipping_country_code"]').val(),
                };
            }).catch((err) => {
                console.log("Error while creating transaction ---", err)
            });
        }
    },
    checkout_override: function () {

        var self = this;
        var loader = $('#paypal_express_loader');
        paypal.Buttons({
            style: self.get_btn_style(),
            onInit(data, actions) {
                // Disable the buttons
                if (!self._paypal_isTCCheckboxReady()) {
                    actions.disable();
                    $('#paypal-button').css("opacity", '0.5')
                    const checkbox = document.querySelector('#website_sale_tc_checkbox');
                    if (checkbox) {
                        checkbox.addEventListener("change", function (event) {
                            if (event.target.checked) {
                                actions.enable();
                                $('#paypal-button').css("opacity", '1')
                            } else {
                                actions.disable();
                                $('#paypal-button').css("opacity", '0.5')
                            }
                        });
                    }
                }

            },

            createOrder: function (data, actions) {
                loader.show();
                return self.order_values().then(function (values) {
                    loader.hide();
                    return actions.order.create({
                        payer: get_payer_data(values),
                        purchase_units: [{
                            amount: {
                                value: values.amount,
                                currency_code: values.currency_code
                            },
                            description: values.so_reference,
                            reference_id: values.reference,
                            shipping: get_shipping_data(values),
                        }],
                    });
                });
            },
            onApprove: function (data, actions) {
                loader.show();
                return actions.order.capture()
                    .then(function (details) {
                        jsonrpc('/paypal/express/checkout/state', details).then(function (result) {
                            window.location.href = window.location.origin + result
                            loader.hide();
                        });
                    });
            },
            onCancel: function (data, actions) {
                loader.show();
                jsonrpc('/paypal/express/checkout/cancel', data).then(function (result) {
                    window.location.href = window.location.origin + result
                    loader.hide();
                });
            },
            onError: function (error) {
                loader.hide();
                alert(error);
                //   window.location.reload()
            }
        }).render('#paypal-button');
    },


    start: async function () {
        await this._super(...arguments);

        const $checkedRadios = this.$('input[name="o_payment_radio"]:checked');
        if ($checkedRadios.length === 1) {
            const checkedRadio = $checkedRadios[0];
            this._expandInlineForm(checkedRadio);
            if ($checkedRadios.attr('data-provider-code') == 'paypal_express') {
                $("button[name='o_payment_submit_button']").hide();
                $('#paypal-button').show();
            } else {
                this._enableButton();
            }
        } else {
            this._setPaymentFlow(); // Initialize the payment flow to let acquirers overwrite it
        }
    },
    _paypal_isTCCheckboxReady() {
        const checkbox = document.querySelector('#website_sale_tc_checkbox');
        if (!checkbox) {
            return true;
        }

        return checkbox.checked;
    },
    _selectPaymentOption: function () {
        this._super.apply(this, arguments);
        var checked_radio = this.$('input[type="radio"]:checked');
        if (checked_radio.length !== 1) {
            return;
        }

        checked_radio = checked_radio[0];
        var provider = checked_radio.dataset.providerCode
        if (provider == 'paypal_express') {
            $("button[name='o_payment_submit_button']").hide();

            if ($("input[name='delivery_type']:checked").length && $("input[name='delivery_type']:checked").parent().find('.o_wsale_delivery_carrier_error').length) {
                $('#paypal-button').hide()
            } else {
                $('#paypal-button').show();
            }
        }
        else {
            $('#paypal-button').hide();
            $("button[name='o_payment_submit_button']").show();
        }

    },
});
