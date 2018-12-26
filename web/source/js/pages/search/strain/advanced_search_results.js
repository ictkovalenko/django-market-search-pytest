'use strict';

W.ns('W.pages');

W.pages.AdvancedSearchFormPage = Class.extend({

    fields: ['thc_from', 'thc_to', 'thca_from', 'thca_to', 'cbc_to', 'cbn_to', 'cbn_from',
             'thcv_from', 'thcv_to', 'cbd_from', 'cbd_to', 'cbg_from', 'cbg_to', 'cbc_from'],

    ui: {
      $form: $('.search-form')
    },
    
    init: function () {
        this.name = 'AdvancedSearchFormPage';
        this.addFormValidation();
    },

    addFormValidation: function () {
        var rules = {};

        for (var i=0, n=this.fields.length; i<n; i+=1){
            rules[this.fields[i]] = {
              required: false,
              number: true
            }
        }

        this.ui.$form.validate({
            rules: rules,
            errorPlacement: function(error, element) {
                error.insertAfter(element.parents('.form-field-wrapper'));
            }
        });
    }
});

W.pages.AdvancedSearchResultsPage = Class.extend({

    scrollPage: 1,
    scrollSize: 20,
    sortKey: 'sort',
    searchResultsTotal: 0,
    firstRender: false,

    ui: {
        $document: $(document),
        $window: $(window),

        $searchResultFooterRegion: $('.search-result-footer-wrapper'),
        $searchContainer: $('.search-container'),
        $loadingIcon: $('.scroll-icon i'),

        searchHeader: '.search-result-header-wrapper',
        menuLinkWrapper: '.filter-menu-wrapper',
        menuLink: '.filter-menu-wrapper .form-field',

        searchResult: '.search-result',
        similarResult: '.similar-result',
        resultItem: '.result-item'
    },

    init: function (options) {
        var that = this;
        this.name = 'AdvancedSearchResultsPage';
        this.isEmailVerified = options.isEmailVerified;
        this.currentUserId = options.currentUserId;
        this.search = new URLSearchParams(window.location.search);
        this.terpenesAbbreviation = JSON.parse(options.terpenesAbbreviation);

        this.getSearchResults(function () {
            that.buildResultsFilterMenu();
            if (!that.currentUserId) {
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

    getSearchResults: function getSearchResults(success) {
        var that = this;
        this.ui.$loadingIcon.addClass('rotating');

        $.ajax({
            method: 'GET',
            url: '/api/v1/search/search/?{0}&page={1}&size={2}'
                .format(window.location.search.slice(1), that.scrollPage, that.scrollSize),
            dataType: 'json',
            error: function () {
                that.ui.$searchResultFooterRegion.addClass('hidden');
                that.ui.$searchContainer.append(
                    '<div class="search-result-subtitle">There was an error processing your request please try again at a later</div>');
            },
            success: function (data) {
                var searchResults = data.list || [];
                var similarResults = (data.similar_vts && data.similar_vts.list) || [],
                    i, position, $searchResult, $similarResult,
                    isBasicSearch = data.hasOwnProperty('similar_vts');

                that.searchResultsTotal = data.total;
                that.ui.$searchResultFooterRegion.addClass('hidden');

                if (!that.firstRender) {
                    that.ui.$searchContainer.html(that.parseSearchResultList(
                        isBasicSearch, similarResults, searchResults, data.q));
                    that.firstRender = true;
                }

                $searchResult = $(that.ui.searchResult);
                $similarResult = $(that.ui.similarResult);

                for (i = 0; i < searchResults.length; i++) {
                    position = '{0}{1}'.format(that.scrollPage, i);
                    $searchResult.append(that.parseSearchResultItem(position, searchResults[i], isBasicSearch));
                }
                for (i = 0; i < similarResults.length; i++) {
                    position = '{0}{1}'.format(that.scrollPage, i);
                    $similarResult.append(that.parseSearchResultItem(position, similarResults[i]));
                }

                that.ui.$loadingIcon.removeClass('rotating');
                that.scrollPage += 1;

                if(success) {
                    success();
                }

                that.totalResultCount = $(that.ui.resultItem).length;
                that.handleScrollPage();
            }
        });

        setTimeout(function () {
            $('#loading-spinner').hide();
        }, 500);
    },

    buildResultsFilterMenu: function buildResultsFilterMenu() {
        var that = this,
            currentFilter = that.search.getAll(that.sortKey),
            $menuLink = $(that.ui.menuLink);
        currentFilter = currentFilter.length ? currentFilter : [''];
        that.ui.$menuLinkWrapper = $(that.ui.menuLinkWrapper);

        $.each($menuLink, function () {
            var $el = $(this);

            if (currentFilter.indexOf($el.data('filter')) !== -1) {
                $el.addClass('active');
            } else {
                $el.removeClass('active');
            }
        });

        $(that.ui.menuLinkWrapper).on('click', '.form-field', function (e) {
            e.preventDefault();
            var $el = $(this);

            that.search.delete(that.sortKey);
            $(that.ui.menuLink).removeClass('active');
            $el.addClass('active');
            that.search.append(that.sortKey, $el.data('filter'));

            window.history.pushState({}, '', '?' + that.search.toString());
            that.applyNewFilter();
        });
    },

    applyNewFilter: function applyNewFilter() {
        this.scrollPage = 1;
        this.ui.$window.off('scroll');
        $(this.ui.searchResult).empty();
        this.ui.$searchResultFooterRegion.removeClass('hidden');
        this.getSearchResults();
    },

    handleScrollPage: function () {
        var that = this;

        this.ui.$window.on('scroll', function () {
            if (that.ui.$window.scrollTop() >= (that.ui.$document.height() - that.ui.$window.height()) * 0.6 &&
                that.searchResultsTotal > that.totalResultCount) {
                that.ui.$window.off('scroll');
                that.getSearchResults();
            }
        });
    },

    parseSearchResultList: function (isBasicSearch, similar_vts, searchResults, q) {
        var compiled = _.template($('#vt-result-template').html());

        return compiled({
            'isBasicSearch': isBasicSearch,
            'similarResult': similar_vts,
            'searchResults': searchResults,
            'q': q,
            'searchParams': window.location.search.slice(1)
        });
    },

    parseSearchResultItem: function (position, item, isBasicSearch) {
        var that = this,
            compiled = _.template($('#vt-item-template').html());

        return compiled({
            'obfuscated': !Boolean(that.currentUserId) || !that.isEmailVerified,
            'position': position,
            'vt': item,
            'terpenesAbbreviation': that.terpenesAbbreviation,
            'price_format': that.formatPrice,
            'distance': that.formatDistance(item.distance),
            'isBasicSearch': isBasicSearch,
            'searchParams': window.location.search.slice(1)
        });
    },

    formatPrice: function (p) {
        return p && p !== 'Infinity' ? '${0}'.format(p) : null;
    },
    formatDistance: function (distance) {
        return distance && distance !== 'Infinity' ? '{0}'.format(Math.round(distance * 10) / 10) : null;
    }
});
