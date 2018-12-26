'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessMenuView = function () {

    var BusinessMenu = W.pages.business.BusinessMenu;

    return {
        init: function (options) {
            new BusinessMenu(options);
        }
    };
}();
