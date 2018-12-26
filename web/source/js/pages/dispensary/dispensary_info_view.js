'use strict';

W.ns('W.pages.dispensary');

W.pages.dispensary.DispensaryInfoView = function () {

    var DispensaryInfo = W.pages.dispensary.DispensaryInfo;

    return {
        init: function (options) {
            new DispensaryInfo(options);
        }
    };
}();
