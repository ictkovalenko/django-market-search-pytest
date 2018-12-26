'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessPartnershipsView = function () {

    var BusinessPartnerships = W.pages.business.BusinessPartnerships;

    return {
        init: function (options) {
            new BusinessPartnerships(options);
        }
    };
}();
