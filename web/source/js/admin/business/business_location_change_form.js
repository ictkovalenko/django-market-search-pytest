(function ($) {

    var BusinessLocationChangeForm = W.views.BaseLocationView.extend({

        ui: {
            $location: $('#id_location_field'),
            $street: $('#id_street1'),
            $city: $('#id_city'),
            $state: $('#id_state'),
            $zipcode: $('#id_zip_code'),
            $latitude: $('#id_lat'),
            $longitude: $('#id_lng'),
            $location_raw: $('#id_location_raw')
        },

        init: function init() {
            this.$input = this.ui.$location.get(0);
            this.autocomplete = new google.maps.places.Autocomplete(this.$input);

            this.initLocationField();

            this.disableInput(this.ui.$street);
            this.disableInput(this.ui.$city);
            this.disableInput(this.ui.$state);
            this.disableInput(this.ui.$zipcode);
            this.disableInput(this.ui.$latitude);
            this.disableInput(this.ui.$longitude);
            this.disableInput(this.ui.$location_raw);

            this.preFillLocationInput();
        },

        disableInput: function ($input) {
            $input.addClass('disabled').attr('tabindex', '-1');
        },

        preFillLocationInput: function () {
            this.ui.$location.val(this.formatAddress({
                street1: this.ui.$street.val(),
                city: this.ui.$city.val(),
                state: this.ui.$state.val(),
                zipcode: this.ui.$zipcode.val(),
                location_raw: this.ui.$location_raw.val()
            }));
        },

        initLocationField: function initLocationField() {
            var that = this;

            google.maps.event.addDomListener(this.$input, 'keydown', function (e) {
                if (e.keyCode === 13) {
                    e.preventDefault();

                    var place = that.autocomplete.getPlace();
                    if (!place || !place.address_components) {
                        that.getAddressFromFirstPacRow();
                    }
                }
            });

            this.autocomplete.addListener('place_changed', function () {
                that.handlePlaceChange(that.autocomplete);
            });
        },

        getAddressFromAutocomplete: function getAddressFromAutocomplete() {
            var that = this, place = this.autocomplete.getPlace();

            if (place && place.address_components) {
                return this.getAddressFromPlace(place);
            } else {
                that.getAddressFromFirstPacRow();
            }
        },

        getAddressFromFirstPacRow: function getAddressFromFirstPacRow() {
            var that = this,
                firstResult = $('.pac-container .pac-item:first').text(),
                geoCoder = new google.maps.Geocoder();

            geoCoder.geocode({"address": firstResult}, function (results, status) {
                if (status === 'OK') {
                    that.handlePlaceChange(results[0]);
                }
            });
        },

        handlePlaceChange: function (result_source) {
            var that = this,
                a = this.getAddressFromAutocomplete(result_source);

            if (!a || !a.street1 || !a.city || !a.state || !a.zipcode) {
                alert('Enter an address with street, city, state and zipcode.');
            } else {
                that.ui.$street.val(a.street1);
                that.ui.$city.val(a.city);
                that.ui.$state.val(a.state);
                that.ui.$zipcode.val(a.zipcode);
                that.ui.$latitude.val(a.lat);
                that.ui.$longitude.val(a.lng);
                that.ui.$location_raw.val(a.location_raw ? JSON.stringify(a.location_raw) : {});

                that.getTimezone(a.lat, a.lng, function (json) {
                    console.log('handlePlaceChange');
                    console.log(json.timeZoneId);
                });
            }
        },

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
    });

    $(document).ready(function () {
        new BusinessLocationChangeForm();
    });

})(django.jQuery);
