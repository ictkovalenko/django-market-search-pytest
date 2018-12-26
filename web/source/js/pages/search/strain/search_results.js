'use strict';

W.ns('W.pages');

W.pages.VtSearchResultsPage = Class.extend({

    scrollPage: 1,
    scrollSize: 20,
    currentFilter: 'local', // local, delivery
    currentSort: 'asc',

    locations: {},
    deliveries: {},

    templates: {
        expandedLocations: _.template($('#expanded-locations-template').html()),
        expandedLocation: _.template($('#expanded-location-template').html())
    },

    ui: {
        $document: $(document),
        $window: $(window),
        $searchResultFooterRegion: $('.search-result-footer-wrapper'),

        $menuExpander: $('.menu-expander'),
        $menuHiddenLinks: $('.hidden-links'),
        $menuFilter: $('.filter-menu'),
        $menuLink: $('.menu-link'),
        $menuActiveLink: $('.menu-active-link a'),

        $vtRating: $('.vt-rating'),
        $searchResult: $('.search-result'),
        $loadingIcon: $('.scroll-icon i')
    },

    init: function (options) {
        var currentUserId = this.getCurrentUserId();
        var that = this;
        this.name = 'VtSearchResultsPage';
        this.settings = new W.users.UserSettings({ userId: currentUserId });
        this.isEmailVerified = options.isEmailVerified;

        that.getSearchResults(that.currentFilter, function () {
            that.buildResultsFilterMenu();
            that.initRatings();

            that.settings.update(that.settings.settingName_SearchFilter, {
                'searchFilter': that.currentFilter
            });

            if (!currentUserId) {
                that.showLoginDialog();
            } else if (!that.isEmailVerified) {
                that.showVerifyDialog();
            }
        });

        W.subscribe.apply(this);
    },

    showLoginDialog: function showLoginDialog() {
        $('#results-ready-dialog').css('display', 'initial');
    },

    showVerifyDialog: function showVerifyDialog() {
        $('#email-verify-dialog').css('display', 'initial');

        var callApi = function() {
            var firstParagraph = $('#email-verify-dialog p:first-of-type');
            firstParagraph.text('Sending email..');

            $.ajax({
                method: 'GET',
                url: '/api/v1/users/resend-email-confirmation'
            }).success(function() {
                firstParagraph.text('Email sent successfully.');
            }).fail(function() {
                firstParagraph.html(
                    "There was a problem with sending your email.\n" +
                    '<a id="resend-email-link" href="#">Click here</a> to resend it.'
                );
                $('#resend-email-link').on('click', callApi);
            });
        };

        $('#resend-email-link').on('click', callApi);
    },

    getCurrentUserId: function getCurrentUserId() {
        var userId = $('#currentUserId').val();
        if (userId === 'None') {
            return undefined;
        }

        return userId;
    },

    _on_close_popup: function _on_close_popup() {
        this.closeOpenedLocationDropdowns();
    },

    closeOpenedLocationDropdowns: function closeOpenedLocationDropdowns() {
        var $menuExpanderButtons = $('.item-locations, .item-deliveries'),
            $expandedAreas = $('.locations-expanded');

        $.each($menuExpanderButtons, function (i, el) {
            var $this = $(el);
            $this.removeClass('expanded');
            $this.css('z-index', 0);
        });

        $.each($expandedAreas, function (i, el) {
            var $this = $(el);
            $this.addClass('hidden');
            $this.html('');
        });
    },

    getSearchResults: function getSearchResults(filterType, success) {
        var that = this;
        this.ui.$loadingIcon.addClass('rotating');
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/result/?filter={0}&page={1}&size={2}'.format(filterType, that.scrollPage, that.scrollSize),
            dataType: 'json',
            error: function () {
                that.ui.$searchResultFooterRegion.addClass('hidden');
                that.ui.$searchResult.append(
                    '<h2>There was an error processing your request please try again at a later</h2>');
            },
            success: function (data) {
                var searchResults = data.search_results,
                    searchResultsTotal = data.search_results_total;

                if (that.scrollPage * that.scrollSize >= searchResultsTotal) {
                    $('.search-result-footer-wrapper').addClass('hidden');
                }

                if (searchResults.length === 0 && searchResultsTotal === 0) {
                    that.ui.$searchResult.append('<h2>No Results Found</h2>');
                } else {
                    for (var i = 0; i < searchResults.length; i++) {
                        var position = '{0}{1}'.format(that.scrollPage, i);

                        that.ui.$searchResult.append(that.parseSearchResultItem(position, searchResults[i]));

                        that.locations[position] = searchResults[i].locations;
                        that.deliveries[position] = searchResults[i].deliveries;

                        that.initRating($('.loaded-rating-{0}'.format(position)));
                        that.clickLocations($('.locations-{0}'.format(position)), position, true);
                        that.clickLocations($('.deliveries-{0}'.format(position)), position, false);
                    }

                    that.ui.$loadingIcon.removeClass('rotating');
                    that.scrollPage += 1;
                }

                if (success) {
                    success();
                }

                that.handleScrollPage();
            }
        });

        setTimeout(function () {
            $('#loading-spinner').hide();
        }, 500);
    },

    buildResultsFilterMenu: function buildResultsFilterMenu() {
        var that = this;

        that.ui.$menuActiveLink.attr('filter', that.currentFilter);
        $.each(that.ui.$menuLink, function () {
            var $menuLink = $(this);
            if ($menuLink.attr('filter') === that.currentFilter) {
                that.ui.$menuActiveLink.text($menuLink.text());
            }
        });


        that.ui.$menuExpander.on('click', function () {
            that.ui.$menuHiddenLinks.toggleClass('hidden');
            that.ui.$menuFilter.toggleClass('expanded');
        });

        that.ui.$menuFilter.mouseleave(function () {
            that.ui.$menuHiddenLinks.addClass('hidden');
            that.ui.$menuFilter.removeClass('expanded');
        });

        that.ui.$menuLink.on('click', function (e) {
            e.preventDefault();
            var $el = $(this),
                filter = $el.attr('filter');

            that.ui.$menuActiveLink.text($el.find('a').text());
            that.ui.$menuActiveLink.attr('filter', filter);
            that.ui.$menuFilter.removeClass('expanded');
            that.ui.$menuHiddenLinks.addClass('hidden');
            that.applyNewFilter(filter);
        });

        that.ui.$menuActiveLink.on('click', function (e) {
            e.preventDefault();
            that.ui.$menuHiddenLinks.toggleClass('hidden');
            that.ui.$menuFilter.toggleClass('expanded');
        });
    },

    applyNewFilter: function applyNewFilter(filter) {
        this.scrollPage = 1;
        this.locations = {};
        this.deliveries = {};
        this.ui.$searchResult.html('');
        this.currentFilter = filter;
        this.ui.$searchResultFooterRegion.removeClass('hidden');
        var that = this;

        this.getSearchResults(this.currentFilter, function () {
            that.settings.update(that.settings.settingName_SearchFilter, {
                'searchFilter': filter
            });
        });
    },

    handleScrollPage: function () {
        var that = this;
        this.ui.$window.on('scroll', function () {
            var hasMoreResultToShow = !that.ui.$searchResultFooterRegion.hasClass('hidden');
            if (that.ui.$window.scrollTop() >= (that.ui.$document.height() - that.ui.$window.height()) * 0.6 && hasMoreResultToShow) {
                that.ui.$window.off('scroll');
                that.getSearchResults(that.currentFilter);
            }
        });
    },

    parseSearchResultItem: function (position, item) {
        var that = this,
            compiled = _.template($('#vt-item-template').html());

        return compiled({
            'obfuscated': !Boolean(that.getCurrentUserId()) || !that.isEmailVerified,
            'position': position,
            'vt': item,
            'closestDistance': that.findClosestDistance,
            'openClosedCount': that.countOpenClosed
        });
    },

    findClosestDistance: function findClosestDistance(locations) {
        var distances = [], min;
        if (locations && locations.length > 0) {
            for (var i = 0; i < locations.length; i++) {
                distances.push(locations[i].distance);
            }
            min = Math.min.apply(Math, distances);
            return 'Nearest {0}mi'.format(Math.round(min * 100) / 100);
        }
    },

    countOpenClosed: function countOpenClosed(locations) {
        var opened = [], closed = [];
        if (locations && locations.length > 0) {
            for (var i = 0; i < locations.length; i++) {
                if (locations[i].open) {
                    opened.push(i);
                } else {
                    closed.push(i);
                }
            }

            if (opened.length > 0 && closed.length > 0) {
                return '{0} Open, {1} Closed'.format(opened.length, closed.length);
            }

            if (opened.length > 0 && closed.length == 0) {
                return '{0} Open'.format(opened.length);
            }

            if (opened.length == 0 && closed.length > 0) {
                return '{0} Closed'.format(closed.length);
            }
        }
    },

    initRatings: function () {
        var that = this;
        that.ui.$vtRating.each(function (position, el) {
            that.initRating($(el));
        });
    },

    initRating: function ($el) {
        var rating = $el.text();
        if (rating && rating.indexOf('Not Rated') === -1) {
            W.common.Rating.readOnly($el, {rating: rating});
        }
    },

    clickLocations: function clickLocations($el, position, isLocations) {
        var that = this;
        $el.on('click', function () {
            var $this = $(this),
                position = $this.attr('position'),
                locations = isLocations ? that.locations[position] : that.deliveries[position],
                $exp = isLocations ? $('.locations-expanded-{0}'.format(position)) : $('.deliveries-expanded-{0}'.format(position));

            if (locations.length > 0) {
                if ($this.hasClass('expanded')) {
                    $this.removeClass('expanded');
                    $this.css('z-index', 0);
                    $exp.addClass('hidden');
                    $exp.html('');
                } else {
                    that.closeOpenedLocationDropdowns();
                    that.showLocations($this, $exp, isLocations, locations, position);
                }
            } else {
                that.closeOpenedLocationDropdowns();
            }
        });
    },

    showLocations: function showLocations($this, $exp, isLocations, locations, position) {
        var that = this, $priceExpander, $priceSort;

        $this.addClass('expanded');
        $this.css('z-index', 11);
        $exp.removeClass('hidden');
        $exp.html(that.templates.expandedLocations({
            'locations': locations,
            'vt_id': $('#vt-id-{0}'.format(position)).val(),
            'formatDistance': that.formatDistance,
            'formatPrice': that.formatPrice,
            'renderLocation': that.templates.expandedLocation
        }));

        $.each($exp.find('.location-rating-exp'), function (i, el) {
            that.initRating($(el));
        });

        $priceExpander = $('.price-sort');
        $priceExpander.on('click', function () {
            $('.prices-wrapper').toggleClass('hidden');
        });

        $('.prices-wrapper').mouseleave(function () {
            $(this).addClass('hidden');
        });

        $('.price').on('click', function () {
            $('.prices-wrapper').addClass('hidden');
            var priceType = $(this).attr('id');
            that.sortByPrice(priceType, isLocations, position, false);
        });

        $priceSort = $('.price-expander');
        $priceSort.on('click', function () {
            that.sortByPrice($('.price-value.active').attr('id'), isLocations, position, true);
        });
    },

    renderLocation: function renderLocation(location) {
        return this.templates.expandedLocation({
            'l': location,
            'vt_id': this.vt_id,
            'formatDistance': this.formatDistance,
            'formatPrice': this.formatPrice
        });
    },

    sortByPrice: function sortByPrice(sortFieldName, isLocations, position, changeSortOrder) {
        var that = this, url;

        if (changeSortOrder) {
            this.currentSort = this.currentSort === 'asc' ? 'desc' : 'asc';
        }

        url = '/api/v1/search/vt/{0}/deliveries?filter={1}&order_field={2}&order_dir={3}&location_type={4}'
            .format($('#vt-id-{0}'.format(position)).val(), this.ui.$menuActiveLink.attr('filter'),
                sortFieldName, this.currentSort, isLocations ? 'dispensary' : 'delivery');

        $.ajax({
            method: 'GET',
            url: url,
            success: function (data) {
                if (data && data.locations) {
                    var $expandedHolder = $('.expanded-locations-holder');
                    $expandedHolder.html('');

                    $.each(data.locations, function (i, l) {
                        $expandedHolder.append(that.renderLocation(l));
                    });

                    $.each($expandedHolder.find('.location-rating-exp'), function (i, el) {
                        that.initRating($(el));
                    });

                    $('.price-value').each(function (index, $el) {
                        var $price = $($el);
                        if ($price.attr('id') === sortFieldName) {
                            $price.addClass('active');
                        } else {
                            $price.removeClass('active');
                        }
                    });
                }
            }
        });
    },

    formatDistance: function formatDistance(d) {
        return '({0}mi)'.format(Math.round(d * 100) / 100);
    },

    formatPrice: function formatPrice(p) {
        return p ? '${0}'.format(p) : 'n/a';
    }
});
