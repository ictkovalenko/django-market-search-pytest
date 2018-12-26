'use strict';

function callback (){}

W.ns('W.views');

// using john resig's simple class inheritence see http://ejohn.org/blog/simple-javascript-inheritance/
W.views.BaseView = Class.extend({

    init: function () {
        var that = this;
    },

    show: function () {
        this.elem.fadeIn();
    },

    hide: function () {
        this.elem.hide();
    }
});


W.views.BaseLocationView = Class.extend({

    getTimezone: function getTimezone(lat, lng, callback) {
        var xsr = new XMLHttpRequest();
        xsr.open(
            'GET',
            'https://maps.googleapis.com/maps/api/timezone/json?location={0},{1}&timestamp={2}&key={3}'
                .format(lat, lng, '1458000000', GOOGLE_API_KEY));

        xsr.onload = function () {
            callback(JSON.parse(xsr.responseText));
        };

        xsr.send();
    },

    buildAddress: function buildAddress(results) {
        if (results.length) {
            return this.getAddressFromPlace(results[0]);
        }
        return {city: '', state: '', zipcode: '', street1: ''}
    },

    getAddressFromPlace: function getAddressFromPlace(raw_place) {
        var street1 = '', zipcode = '', state = '', city = '', aal3 = '';
        $.each(raw_place.address_components, function (i, address_comp) {
            if (_.includes(address_comp.types, 'street_number')) {
                street1 += address_comp.long_name + ' ';
            }

            if (_.includes(address_comp.types, 'route')) {
                street1 += address_comp.long_name;
            }

            if (_.includes(address_comp.types, 'postal_code') && zipcode === '') {
                zipcode = address_comp.long_name;
            }

            if (_.includes(address_comp.types, 'administrative_area_level_1') && state === '') {
                state = address_comp.short_name;
            }

            if (_.includes(address_comp.types, 'locality') && city === '') {
                city = address_comp.long_name;
            }

            if (_.includes(address_comp.types, 'administrative_area_level_3') && aal3 === '') {
                aal3 = address_comp.long_name;
            }
        });

        return {
            street1: street1,
            city: city || aal3,
            state: state,
            zipcode: zipcode,
            lat: raw_place.geometry && raw_place.geometry.location.lat(),
            lng: raw_place.geometry && raw_place.geometry.location.lng(),
            location_raw: JSON.stringify(raw_place)
        };
    },

    getLocation: function getLocationAddress(success, failure) {
        var that = this;

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                var geoCoder = new google.maps.Geocoder(),
                    pos = {lat: position.coords.latitude, lng: position.coords.longitude};

                geoCoder.geocode({'location': pos}, function (results, status) {
                    if (status === 'OK') {
                        if (results) {
                            var address = that.buildAddress(results);
                            that.getTimezone(position.coords.latitude, position.coords.longitude, function (json) {
                                success({
                                    address: {
                                        lat: position.coords.latitude,
                                        lng: position.coords.longitude,
                                        location_raw: JSON.stringify(results),
                                        street1: address.street1,
                                        city: address.city,
                                        state: address.state,
                                        zipcode: address.zipcode
                                    },
                                    timezone: json.timeZoneId || ''
                                });
                            });
                        }
                    } else {
                        that.getLocationByIP(success, failure)
                    }
                });
            }, function () {
                return that.getLocationByIP(success, failure)
            });
        } else {
            this.getLocationByIP(success, failure)
        }
    },
    
    getLocationByIP: function (success, failure) {
        var that = this;

        $.ajax({
            url: 'https://geoip-db.com/jsonp',
            dataType: 'jsonp',
            jsonp: 'callback',
            jsonpCallback: 'callback',
            success: function (location) {
                that.getTimezone(location.latitude, location.longitude, function (json) {
                    success({
                        address: {
                            lat: location.latitude,
                            lng: location.longitude,
                            location_raw:'',
                            street1: '',
                            city: location.city,
                            state: location.state,
                            zipcode: location.postal
                        },
                        timezone:  json.timeZoneId || ''
                    });
                })
            }
        });

        failure()
    }
});
