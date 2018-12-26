'use strict';

W.ns('W.pages.locations');

W.pages.locations.LocationsListView = function () {

    var LocationsList = W.pages.locations.LocationsList;

    return {
        init: function init(options) {
            new LocationsList(options);
        }
    };
}();
