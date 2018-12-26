'use strict';

W.ns('W.pages.vt');

W.pages.vt.VtsRootView = function () {

    var VtsRootPage = W.pages.vt.VtsRootPage;

    return {
        init: function (options) {
            new VtsRootPage(options);
        }
    };
}();
