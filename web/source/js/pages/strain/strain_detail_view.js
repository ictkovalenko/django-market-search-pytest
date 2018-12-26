'use strict';

W.ns('W.pages.vt');

W.pages.vt.VtDetailView = function () {

    var VtDetailPage = W.pages.vt.VtDetailPage;

    return {
        init: function (options) {
            new VtDetailPage(options);
        }
    };
}();
