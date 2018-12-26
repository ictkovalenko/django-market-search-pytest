'use strict';

W.ns('W.common');

W.common.Format = {

    formatAddress: function formatAddress(location) {
        if (location) {
            var l = [];

            if (location.street1) {
                l.push(location.street1);
            }

            if (location.city) {
                l.push(location.city);
            }

            if (location.state) {
                l.push(location.state);
            }

            if (location.zipcode) {
                l.push(location.zipcode);
            }

            if (l.length === 0 && location.location_raw && !_.isEmpty(l.location_raw)) {
                var parsed = JSON.parse(location.location_raw);
                if (parsed && parsed[0] && parsed[0].formatted_address) {
                    l.push(parsed[0].formatted_address);
                }
            }

            return l.join(', ');
        }

        return '';
    }

};
