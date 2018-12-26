'use strict';

W.ns('W.pages.vt');

W.pages.vt.VtLookup = Class.extend({

    init: function init(options) {
        this.onArrowUp = options && options.onArrowUp;
        this.onArrowDown = options && options.onArrowDown;
        this.onReturn = options && options.onReturn;
        this.onSelectCallback = options && options.onSelect;

        this.changeLookupInput();
        this.clickOutsidePayloadArea();
    },

    changeLookupInput: function changeLookupInput() {
        var that = this;
        $('.lookup-input').on('keyup', function (e) {
            var text = $(this).val(),
                $payloadsRegion = $('.payloads-region'),
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
                $payloadsRegion.css('display', 'none');
                that.onEnterKeyPress(e, $activePayload, $firstPayload, $lastPayload);
                return;
            }

            if (text && text.length >= 1) {
                $.ajax({
                    method: 'GET',
                    url: '/api/v1/search/vt/lookup/?q={0}'.format(encodeURIComponent(text)),
                    success: function (data) {
                        $payloadsRegion.html('');
                        $payloadsRegion.append(that.buildPayloadLookupArea(data));
                        $payloadsRegion.css('display', 'block');

                        $('.search-payload').on('click', function () {
                            that.onSelect($(this));
                        });
                    }
                });
            } else {
                $payloadsRegion.html('');
                $payloadsRegion.css('display', 'none');
            }
        });
    },

    onSelect: function onSelect($activePayload) {
        if (!$activePayload || $activePayload.length === 0) {
            return;
        }

        var $lookupInput = $('.lookup-input'),
            $payloadsRegion = $('.payloads-region');

        var selected = {
            id: $activePayload.attr('id'),
            slug: $activePayload.attr('slug'),
            variety: $activePayload.attr('variety')
        };

        $lookupInput.attr('payload-id', selected.id);
        $lookupInput.attr('payload-slug', selected.slug);
        $lookupInput.attr('payload-variety', selected.variety);
        $lookupInput.val($activePayload.text());

        $payloadsRegion.html('');

        if (this.onSelectCallback) {
            this.onSelectCallback(selected);
        }
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

    onEnterKeyPress: function onEnterKeyPress(e, $activePayload, $firstPayload, $lastPayload) {
        e.preventDefault();

        this.onSelect($activePayload);

        if (this.onReturn) {
            this.onReturn($activePayload, $firstPayload, $lastPayload);
            return;
        }
    },

    buildPayloadLookupArea: function buildPayloadLookupArea(data) {
        if (data) {
            var totalResults = data.total,
                payloads = data.payloads,
                itemHtml = '<span class="search-payload" id="{0}" slug="{1}" variety="{2}">{3}</span>',
                payloadHtml = '';

            if (totalResults && totalResults > 0) {
                $.each(payloads, function (index, payload) {
                    payloadHtml += itemHtml.format(payload.id, payload.vt_slug, payload.variety, payload.name);
                });
                return payloadHtml;
            }
        }
    },

    clickOutsidePayloadArea: function clickOutsidePayloadArea() {
        $(document).on('click', function (e) {
            var elem = $(e.target);
            if (!(elem.parents('.payloads-region').length)) {
                $('.payloads-region').html('');
                $('.payloads-region').css('display', 'none');
            }
        });
    }
});
