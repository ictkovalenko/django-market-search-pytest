'use strict';

W.ns('W.Common');

W.Common.GoogleLocations = W.views.BaseLocationView.extend({

    init: function init(options) {
        if (!options || !options.$input) {
            console.error('$input is required to use location autocomplete');
        }

        this.$input = options && options.$input;
        this.autocomplete = new google.maps.places.Autocomplete(this.$input);
        this.pacContainerIndex = options && options.pacContainerIndex;
    },

    initGoogleAutocomplete: function initGoogleAutocomplete(onPlaceChange, onEnterKey, onLocationRemove) {
        var that = this,
            onLocationRemoveFunction = function () {
                if (that.$input.value && that.onLocationRemove) {
                    that.onLocationRemove(that.$input);
                }
            };

        this.onPlaceChange = onPlaceChange;
        this.onEnterKey = onEnterKey;
        this.onLocationRemove = onLocationRemove;

         onLocationRemoveFunction();

         google.maps.event.addListener(that.autocomplete, 'place_changed', function () {
                var place = that.autocomplete.getPlace();
                if (!place || !place.address_components) {
                    var firstResult, $pacs,
                        geoCoder = new google.maps.Geocoder();

                    if (that.pacContainerIndex && that.pacContainerIndex >= 0) {
                        $pacs = $('.pac-container');
                        firstResult = $($pacs[that.pacContainerIndex]).find('.pac-item:first').text()
                    } else {
                        firstResult = $('.pac-container .pac-item:first').text();
                    }
                    geoCoder.geocode({"address": firstResult}, function (results, status) {
                        if (that.onEnterKey) {
                            that.onEnterKey(results, status, that.$input);
                        }
                    });
                } else {
                    that.onPlaceChange(that.autocomplete, that.$input);
                }

                onLocationRemoveFunction();
        });

        $(this.$input).on('change paste keyup', function (e) {
            onLocationRemoveFunction();
        });
    },

    getAddressFromAutocomplete: function getAddressFromAutocomplete() {
        var that = this, place = this.autocomplete.getPlace();

        if (place && place.address_components) {
            return this.getAddressFromPlace(place);
        } else {
            var firstResult, $pacs,
                geoCoder = new google.maps.Geocoder();

            if (this.pacContainerIndex && this.pacContainerIndex >= 0) {
                $pacs = $('.pac-container');
                firstResult = $($pacs[this.pacContainerIndex]).find('.pac-item:first').text()
            } else {
                firstResult = $('.pac-container .pac-item:first').text();
            }

            geoCoder.geocode({"address": firstResult}, function (results, status) {
                if (status !== 'OK') {
                    alert('Invalid address');
                } else {
                    if (this.onEnterKey) {
                        this.onEnterKey(results, status, that.$input);
                    }
                }
            });
        }
    }
});
