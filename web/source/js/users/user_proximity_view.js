'use strict';

W.ns('W.users');

W.users.ProximityView = function () {

    var ProximityPage = W.users.ProximityPage;

    return {
        init: function (options) {
            new ProximityPage(options);
        }
    };
}();
