'use strict';

W.ns('W');

var Navbar = W.views.BaseLocationView.extend({
    init: function init(options) {
        var that = this;
        options = options || {};

        that.authenticated = options.authenticated;
        that.location = options.location;
        that.userId = options.userId;

        if (that.authenticated && options.locationUpdate || !that.authenticated) {
            that.getLocation(
                function(location) {
                    that.location = location;
                    that.updateAddress(location.address);
                    that.clickUpdateLocation();
                    $('.update-location-href').removeClass('hidden');
                },
                function() {
                    $('.action.location').addClass('hidden');
                }
            );
        }

        this.hamburgerMenuClickHandler();
    },

    updateAddress: function (location) {
        var location_parts = [];
        if (!location) {
            return;
        }

        $('.nav-bar-user-street').text(location.street1 || '');

        location_parts.push(location.city || '');
        location_parts.push(location.state || '');
        location_parts.push(location.zipcode || '');

        if (location_parts.length === 0 && location.location_raw && !_.isEmpty(location.location_raw)) {
            var parsed = JSON.parse(location.location_raw);
            if (parsed && parsed[0] && parsed[0].formatted_address) {
                location_parts.push(parsed[0].formatted_address);
            }
        }

        $('.nav-bar-user-location').text(location_parts.join(', '));
        this.saveUserLocation(this.location);
    },

    hamburgerMenuClickHandler: function hamburgerMenuClickHandler() {
        var menuSelector = $('.nav-list-wrapper .mobile-menu');

        $(document).click('click tap', function (e) {
            if ($(window).width() > 480) {
                return;
            }

            var $target = $(e.target);
            var navList = $('.nav-list');

            if ($target.is(menuSelector) || $target.closest(menuSelector).length) {
                if (navList.css('display') === 'block') {
                    navList.css('display', 'none');
                } else {
                    navList.css('display', 'block');
                }
            } else {
                navList.css('display', 'none');
            }
        })

    },

    clickUpdateLocation: function clickUpdateLocation() {
        var that = this;
        $('.update-location-href').on('click', function (e) {
            that.saveUserLocation(that.location);
        });
    },

    saveUserLocation: function saveUserLocation(location) {
        var that = this,
            locationRaw = location.address.location_raw,
            $locationInput = $('.your-location-value');

        if (locationRaw) {
            var parsed = JSON.parse(locationRaw);
            if (parsed && parsed[0] && $locationInput) {
                $locationInput.val(parsed[0].formatted_address).trigger('change');
            }
        }

        if (this.authenticated) {
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/{0}/geo_locations'.format(that.userId),
                data: JSON.stringify(location)
            });
        } else {
            delete location.address.location_raw;
            Cookies.set('user_geo_location', JSON.stringify(location.address));
        }
    }
});


W.Navbar = function () {

    return {
        init: function init(options) {
            return new Navbar(options);
        }
    };
}();
