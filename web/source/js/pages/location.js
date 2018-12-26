'use strict';

W.ns('W');

W.Location = function () {

    var LocationView = W.views.LocationView;

    return {
        init: function init(options) {
            new LocationView(options);
        }
    };
}();
