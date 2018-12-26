'use strict';

W.ns('W.pages.locations');

W.pages.locations.LocationsLookupWidget = Class.extend({

    init: function init(options) {
        this.locationType = options.locationType;
        this.onArrowUp = options.onArrowUp;
        this.onArrowDown = options.onArrowDown;
        this.onReturn = options.onReturn;
        this.onChange = options.onChange || function () {};
        this.currentValue = undefined;

        this.changeLookupInput();
        this.initEventHandlers();
        this.clickOutsidePayloadArea();
    },
    initEventHandlers: function initEventHandlers() {
        var that = this;

        $('.payloads-region').on('click', '.search-payload', function (e) {
            var text = $('.lookup-input').val(),
                selectedItem = $(e.currentTarget),
                url = selectedItem.attr('url'),
                business_location_id = selectedItem.attr('business_location_id');

            that.onSelect(e, url, text, business_location_id);
        });
    },
    setCurrentValue: function setCurrentValue(val) {
        this.currentValue = val;
    },

    changeLookupInput: function changeLookupInput() {
        var that = this;

        $('.lookup-input').on('keyup', function (e) {
            var text = $(this).val(),
                $payloadsRegion = $('.payloads-region'),
                url = $payloadsRegion.find('.search-payload.active').attr('url'),
                business_location_id = $payloadsRegion.find('.search-payload.active').attr('business_location_id'),
                $activePayload = $payloadsRegion.find('.search-payload.active'),
                $firstPayload = $payloadsRegion.find('.search-payload:nth-child(1)'),
                $lastPayload = $payloadsRegion.find('.search-payload:last-child');

            if (e.keyCode === 38) { // Up Arrow Key
                that.onArrowUpKeyPress(e, $activePayload, $firstPayload, $lastPayload);
                return;
            }

            if (e.keyCode === 40) { // Down Arrow Key
                that.onArrowDownKeyPress(e, $activePayload, $firstPayload, $lastPayload);
                return;
            }

            if (e.keyCode === 13) { // Enter Key
                that.onSelect(e, url, text, business_location_id);
                return;
            }

            if (text && text.length >= 1) {
                var context = { query: text };
                var url;

                if (that.locationType === 'dispensary') {
                    url = '/api/v1/search/dispensary/lookup/';
                } else {
                    url = '/api/v1/search/grow_house/lookup/';
                }

                if (window.DispensaryPage) {
                    var locTime = DispensaryPage.getLocationTime();
                    context.loc = encodeURIComponent(JSON.stringify(locTime.location));
                    context.tz = encodeURIComponent(JSON.stringify(locTime.timezone));
                    url = url + '?q={query}&loc={loc}&tz={tz}'.format(context);
                } else {
                    url = url + '?q={query}'.format(context);
                }

                $.ajax({
                    method: 'GET',
                    url: url,
                    success: function (data) {
                        $payloadsRegion.html('');
                        $payloadsRegion.append(that.buildPayloadLookupArea(data));
                    }
                });
            } else {
                $payloadsRegion.html('');
                $payloadsRegion.hide();
            }

            that.setCurrentValue();
            that.onChange();
        });
    },

    onArrowUpKeyPress: function onArrowUpKeyPress(e, $activePayload, $firstPayload, $lastPayload) {
        e.preventDefault();

        if (this.onArrowUp) {
            this.onArrowUp($activePayload, $firstPayload, $lastPayload);
            return;
        }

        if ($activePayload && $activePayload.length > 0) {
            if ($activePayload.prev().length > 0) {
                $activePayload.removeClass('active');
                $activePayload.prev().addClass('active');
            }
        } else {
            $lastPayload.addClass('active');
        }
    },

    onArrowDownKeyPress: function onArrowDownKeyPress(e, $activePayload, $firstPayload, $lastPayload) {
        e.preventDefault();

        if (this.onArrowDown) {
            this.onArrowDown($activePayload, $firstPayload, $lastPayload);
            return;
        }

        if ($activePayload && $activePayload.length > 0) {
            if ($activePayload.next().length > 0) {
                $activePayload.removeClass('active');
                $activePayload.next().addClass('active');
            }
        } else {
            $firstPayload.addClass('active');
        }
    },

    onSelect: function onEnterKeyPress(e, url, text, business_location_id) {
        e.preventDefault();

        if (url && text) {
            this.setCurrentValue({ url: url, id: business_location_id});

            var $lookupInput = $('.lookup-input'),
                $payloadsRegion = $('.payloads-region');

            $lookupInput.attr('payload-url', url);
            $lookupInput.attr('business_location_id', business_location_id);
            $lookupInput.val(text);
            $payloadsRegion.html('');
            $payloadsRegion.hide();

            this.onChange(this.currentValue);

        }

    },

    buildPayloadLookupArea: function buildPayloadLookupArea(data) {
        var that = this;
        if (data) {
            var totalResults = data.total,
                payloads = data.payloads,
                itemHtml = '<span class="search-payload" id="{id}" url="{url}" business_location_id="{business_location_id}" name="{name}"><img width="20" height="20" src="{img_src}"/><span class="disp-name">{name}</span> ({loc}) {dist} {open}</span>',
                payloadHtml = '',
                url;

            if (totalResults && totalResults > 0) {
                $.each(payloads, function (index, payload) {
                    if (that.locationType === 'dispensary') {
                        url = payload.urls.dispensary;
                    } else {
                        url = payload.urls.grow_house;
                    }
                    payloadHtml += itemHtml.format({
                        'id': payload.business_location_id,
                        'img_src': payload.image || '{0}images/default-location-image.jpeg'.format(STATIC_URL),
                        'url': url,
                        'name': payload.location_name,
                        'open': (payload.open) ? 'Open' : 'Closed',
                        'loc': '{0}, {1}'.format(payload.city, payload.state),
                        'dist': (payload.distance) ? '{0} Miles'.format(Math.round(payload.distance * 10) / 10) : '',
                        'business_location_id': payload.business_location_id
                    });
                });

                $('.payloads-region').show();

                return payloadHtml;
            }
        } else {
            $('.payloads-region').hide();
        }
    },

    clickOutsidePayloadArea: function clickOutsidePayloadArea() {
        var that = this;

        $(document).on('click', function (e) {
            var elem = $(e.target);

            if (elem.hasClass('search-payload')) {
                // click on autocomplete result
                var url = elem.attr('url'),
                    text = elem.attr('name'),
                    business_location_id = elem.attr('business_location_id');

                that.onSelect(e, url, text, business_location_id);
            } else if (!(elem.parents('.payloads-region').length)) {
                $('.payloads-region').html('');
                $('.payloads-region').hide();

                if (!that.currentValue) {
                    $('#disp-lookup').val(undefined);
                    that.setCurrentValue();
                    that.onChange();
                }
            }
        });
    }
});
