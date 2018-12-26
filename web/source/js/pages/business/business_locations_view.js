'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessLocationsView = function () {

    var BusinessLocations = W.pages.business.BusinessLocations;

    return {
        init: function () {
            new BusinessLocations();
        }
    };
}();
