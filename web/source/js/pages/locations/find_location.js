'use strict';

W.ns('W.pages.locations');

W.pages.locations.FindLocation = Class.extend({
    init: function init(options) {
        this.location = options.location;
        this.locationType = options.locationType;
        this.authenticated = options.authenticated;
        this.userId = options.userId;
        this.defaultImageUrl = options.defaultImageUrl;
        this.dispTimezone = null;
        this.dispLocation = null;
        this.browserInfo = W.detectBrowser();

        this.initLookupField();
        this.initLocationWidget();
        this.initEventHandlers();
        this.ieHack();
    },
    ieHack: function idHack() {
        if (this.browserInfo.type === W.C.IE && this.browserInfo.version <= 11) {
            $('.lookup-submit').css({
                position: 'relative',
                top: '1em'
            });
        }
    },
    initLookupField: function initDispensaryLookupField() {
        var that = this;
        new W.pages.locations.LocationsLookupWidget({
            locationType: that.locationType,
            onChange: function(dispensary) {
                if (dispensary) {
                    that.navigateToDispDetailPage(dispensary);
                }
            }});
    },
    initEventHandlers: function initEventHandlers() {
        var that = this;

        $('.location-location-label').on('click', function (e) {
            e.preventDefault();

            $('.location-location-value').val('loading location...');
            that.clearLocation();

            navigator.geolocation.getCurrentPosition(function (position) {
                var geoCoder = new google.maps.Geocoder(),
                    pos = {lat: position.coords.latitude, lng: position.coords.longitude};

                geoCoder.geocode({'location': pos}, function (results, status) {
                    if (status === 'OK') {
                        if (results) {
                            that.updateLocationTime(that.GoogleLocations, {
                                lat: position.coords.latitude,
                                lng: position.coords.longitude
                            });
                            $('.location-location-value').val(results[0].formatted_address);
                        }
                    } else {
                        console.log('Geocoder failed due to: ' + status);
                        $('.location-location-value').val('');
                    }
                });
            }, function () {
                console.log('Cannot locate user');
                $('.location-location-value').val('');
            });
        });
    },
    initLocationWidget: function initDispLocation() {
        var that = this;
        this.GoogleLocations = new W.Common.GoogleLocations({$input: $('#location-location').get(0)});

        this.GoogleLocations.initGoogleAutocomplete(
            function (autocomplete, $input) {
                var $el = $($input),
                    address = that.GoogleLocations.getAddressFromAutocomplete(autocomplete);

                that.onAddressChange($el, address);
            },
            function (results, status, $input) {
                if (status === 'OK') {
                    var $el = $($input),
                        address = that.GoogleLocations.getAddressFromPlace(results[0]);

                    that.onAddressChange($el, address);
                }
            },
            function ($input) {
                that.clearLocation();
            });
    },
    clearLocation: function clearDispLocation() {
        this.dispLocation = null;
        this.dispTimezone = null;
    },
    navigateToDispDetailPage: function navigateToDispDetailPage(dispensary) {
        W.track({
            event: "DISP_LOOKUP",
            entity_id: dispensary.id
        });

        if (dispensary.url) {
            window.location.href = dispensary.url;
        }
    },
    updateLocationTime: function updateDispLocationTime(GoogleLocations, address) {
        var that = this;

        this.dispLocation = {
            lat: address.lat,
            lon: address.lng
        };

        GoogleLocations.getTimezone(address.lat, address.lng, function (json) {
            that.dispTimezone = json.timeZoneId;
        });
    },
    updateTimezone: function updateTimezone(GoogleLocations, address, success) {
        var that = this;
        GoogleLocations.getTimezone(address.lat, address.lng, function (json) {
            that.timezone = json.timeZoneId;
            success();
        });
    },
    saveUserLocation: function saveUserLocation(data) {
        if (data) {
            var that = this;
            if (this.authenticated) {
                $.ajax({
                    method: 'POST',
                    url: '/api/v1/users/{0}/geo_locations'.format(that.userId),
                    data: JSON.stringify({address: data, timezone: this.timezone})
                });
            } else {
                delete data.location_raw;
                Cookies.set('user_geo_location', JSON.stringify(data));
            }
        }
    },
    getLocationTime: function getDispLocationTime() {
        return {
            location: this.dispLocation,
            timezone: this.dispTimezone
        };
    },
    onAddressChange: function onAddressChange($el, address) {
        var that = this;
        $el.val(W.common.Format.formatAddress(address));
        $el.blur();

        this.updateLocationTime(that.GoogleLocations, address);
        this.fetchFeatured(address).success(function(data) {
            that.renderFeatured(data.locations);
        });
    },
    fetchFeatured: function fetchFeatured(address) {
        var url = '/api/v1/businesses/locations/featured/?loc=';
        var loc = {
            lat: address.lat,
            lon: address.lng
        };

        if (address.zipcode) {
            loc.zip = address.zipcode;
        }

        url = url + encodeURIComponent(JSON.stringify(loc));

        return $.ajax({
            method: 'GET',
            url: url
        });
    },
    renderFeatured: function renderFeatured(locations) {
        var defaultImageUrl = this.defaultImageUrl;
        var templateFn = _.template($('#featured-locations-template').html());
        var html = '';

        locations.forEach(function(location) {
            html += templateFn({
                url: location.url,
                location_name: location.location_name  || 'None',
                image_url: location.image_url || 'None',
                default_image_url: defaultImageUrl || 'None',
                street1: location.street1 || 'None',
                city: location.city || 'None',
                state: location.state || 'None',
                zip_code: location.zip_code || 'None',
                phone: location.phone || 'None',
                location_email: location.location_email || 'None'
            });
        });

        $('.featured-list').html(html);
    }

});
