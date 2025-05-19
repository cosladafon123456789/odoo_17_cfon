odoo.define('sendcloud_delivery.ServicePoint', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');
var ajax = require('web.ajax');

var QWeb = core.qweb;

var SendcloudServicePoint = AbstractField.extend({

    events: {
        'click .o_select_service_point': '_onOpenServicePointWizard',
        'click .o_empty_service_point': '_onEmptyServicePoint',
    },

    supportedFieldTypes: ['text'],
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.point_value = ''
    },

    _render: function () {
        var value = '';
        if (this.value){
            var field_value = JSON.parse(this.value);
            value = field_value.street + ',' + field_value.house_number + ',' + field_value.postal_code + ',' + field_value.city;
        }
        return this.$el.html(QWeb.render('SendCloudServicePointDetails',{self: this,value:value}));
    },

    _onEmptyServicePoint : function (event) {
        this._setValue('');

    },

    _onOpenServicePointWizard: function (event) {
        var self = this;
        ajax.jsonRpc("/web/dataset/call_kw", 'call', {
                model: 'stock.picking',
                method: 'get_details_sendcloud_backend',
                args: [self.recordData.id],
                kwargs: {},
            }).then(function (result) {
                  var config = {
                  apiKey: result['key'],
                  country: result['country_code'],
                  postalCode: result['postcode'],
                  language: 'en-us',
                  carriers: result['carrier_name'],
                  // servicePointId: '8718',
                  // postNumber: sendcloud_details['postcode']
                };
                sendcloud.servicePoints.open(
                  config,
                  function(servicePointObject, postNumber) {
                      var value = JSON.stringify(servicePointObject);
                      self._setValue(value);
                  },
                  function(errors) {
                    errors.forEach(function(error) {
                      console.log('Failure callback, reason: ' + error)
                    })
                  }
        );
            }

        );
    },
});

field_registry.add('backend_sendcloudservicepoint', SendcloudServicePoint);

});
