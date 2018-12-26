'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessAccountView = function () {

    var BusinessAccount = W.pages.business.BusinessAccount;

    return {
        init: function () {
            new BusinessAccount();
        }
    };
}();
