'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessDetailView = function () {

    var BusinessDetail = W.pages.business.BusinessDetail;

    return {
        init: function () {
            new BusinessDetail();
        }
    };
}();
