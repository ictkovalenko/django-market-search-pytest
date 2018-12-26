'use strict';

W.ns('W.pages.dispensary');

W.pages.dispensary.DispensaryInfo = Class.extend({

    location: null,
    dialog: null,

    allReviewsPage: 1,
    allReviewsSize: 5,

    urls: {
        favorite: '/api/v1/businesses/{0}/locations/{1}/favorite',
        location: '/api/v1/businesses/{0}/locations/{1}?ddp=true',
        menu: '/api/v1/businesses/{0}/locations/{1}/menu?ddp=true',
        review: '/api/v1/businesses/{0}/locations/{1}/reviews',
        menuUpdateRequest: '/api/v1/businesses/{0}/locations/{1}/menu-update-requests',
        reportOutOfStock: '/api/v1/businesses/{0}/menu_item/{1}/report-out-of-stock'
    },

    ui: {
        $businessId: $('#business_id'),
        $location_id: $('#location_id'),
        $vt_id: $('#vt_id')
    },

    regions: {
        $headerRegion: $('.header-region'),
        $contentRegion: $('.content-region')
    },

    templates: {
        $header: _.template($('#dispensary_header_template').html()),
        $content: _.template($('#dispensary_content_template').html()),
        $allReviews: _.template($('#dispensary_all_reviews_template').html())
    },

    init: function init(options) {
        var that = this;
        that.isAuthenticated = options.isAuthenticated;
        that.user = options.user;

        this.retrieveLocation(function (location) {
            if (location) {
                that.location = location;
                that.showHeader();
                that.showContent();
            }
        });
    },

    priceIndicator: function (avg_price) {
      if (avg_price < 31) return 1;
      else if (avg_price < 41) return 2;
      else if (avg_price < 51) return 3;
      else if (avg_price < 66) return 4;
      else return 5;
    },

    retrieveLocation: function retrieveLocation(successCallback) {
        $.ajax({
            method: 'GET',
            url: this.urls.location.format(this.ui.$businessId.val(), this.ui.$location_id.val()),
            success: function (data) {
                successCallback(data.location);
            }
        });
    },

    showHeader: function showHeader() {
        var qs = W.qs(),
            search = qs['search'],
            $rawRating,
            $avgPrice;

        this.regions.$headerRegion.append(this.templates.$header({
            from_search: search,
            share_urls: W.common.Sharer.getSharerUrls(encodeURIComponent(window.location.href)),
            l: this.location,
            avg_price: this.priceIndicator(this.location.avg_price),
            formatAddressLine: this.formatAddressLine,
            getOpenDays: this.getOpenDays,
            is_authenticated: AUTHENTICATED
        }));

        $rawRating = $('.rating-raw');
        if ($rawRating && $rawRating.text() === 'Not Rated') {
            $rawRating.addClass('hidden');
        } else {
            W.common.Rating.readOnly($rawRating, {rating: $rawRating.text(), spacing: '5px', starWidth: '20px'});
        }

        $avgPrice = $('.avg-price-indicator');
        W.common.Rating.readOnly($avgPrice, {
            rating: $avgPrice.text(), spacing: '-5px',
            starWidth: '20px',
            starSvg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 288 512"><path d="M209.2 233.4l-108-31.6C88.7 198.2 80 186.5 80 173.5c0-16.3 13.2-29.5 29.5-29.5h66.3c12.2 0 24.2 3.7 34.2 10.5 6.1 4.1 14.3 3.1 19.5-2l34.8-34c7.1-6.9 6.1-18.4-1.8-24.5C238 74.8 207.4 64.1 176 64V16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v48h-2.5C45.8 64-5.4 118.7.5 183.6c4.2 46.1 39.4 83.6 83.8 96.6l102.5 30c12.5 3.7 21.2 15.3 21.2 28.3 0 16.3-13.2 29.5-29.5 29.5h-66.3C100 368 88 364.3 78 357.5c-6.1-4.1-14.3-3.1-19.5 2l-34.8 34c-7.1 6.9-6.1 18.4 1.8 24.5 24.5 19.2 55.1 29.9 86.5 30v48c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-48.2c46.6-.9 90.3-28.6 105.7-72.7 21.5-61.6-14.6-124.8-72.5-141.7z"/></svg>' // dollar sign
        });

        this.clickRateLink();
        this.submitLocationReview();

        this.clickFavoriteIcon();
        this.clickPhoneNumberLink();
        this.clickPlaceOrderBtn();
        this.clickGetDirectionsBtn();
        this.clickAvgPriceIndicator();
    },

    getVtUrl: function getVtUrl(mi) {
        return mi.url;
    },

    formatAddressLine: function formatAddressLine(location) {
        var parts = [];

        if (location.city) {
            parts.push(location.city);
        }

        if (location.state) {
            parts.push(location.state);
        }

        if (location.zip_code) {
            parts.push(location.zip_code);
        }

        return parts.join(', ');
    },

    getOpenDays: function getOpenDays(location) {
        var days = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'],
            dayNames = W.common.Constants.days,
            todayIndex = new Date().getDay(), // 0 - Sun, 6 - Sat
            toDisplay = [],
            open_time, close_time;

        $.each(days.slice(todayIndex, days.length), function (i, day) {
            var d = _.filter(dayNames, function (d) {
                return d.value === day ? d : null;
            });

            if (d && d[0]) {
                open_time = location['{0}_open'.format(d[0].value)];
                close_time = location['{0}_close'.format(d[0].value)];

                toDisplay.push({
                    day: d[0].name,
                    time: (open_time && close_time) ? '{0} - {1}'.format(open_time, close_time) : 'Closed',
                    first: i === 0
                });
            }
        });

        $.each(days.slice(0, todayIndex), function (i, day) {
            var d = _.filter(dayNames, function (d) {
                return d.value === day ? d : null;
            });

            if (d && d[0]) {
                open_time = location['{0}_open'.format(d[0].value)];
                close_time = location['{0}_close'.format(d[0].value)];

                toDisplay.push({
                    day: d[0].name,
                    time: (open_time && close_time) ? '{0} - {1}'.format(open_time, close_time) : 'Closed'
                });
            }
        });

        return toDisplay;
    },

    clickRateLink: function clickRateLink() {
        $('.rate-link').on('click', function (e) {
            e.preventDefault();
            W.common.RateDialog($('.rate-location-dialog'));
        });
    },

    submitLocationReview: function submitLocationReview() {
        var that = this;
        $('.rate-location-form').on('submit', function (e) {
            e.preventDefault();
            var rating = $('.rate-stars').rateYo('rating'),
                review = $('.rate-review').val();

            if (rating === 0) {
                $('.error-message').text('Rating is required');
                return;
            }

            if (review && review.length > 500) {
                $('.error-message').text('Review max length 500 is exceeded');
                return;
            }

            $('.loader').removeClass('hidden');
            $('.btn-review-submit').addClass('hidden');

            $.ajax({
                type: 'POST',
                url: that.urls.review.format(that.ui.$businessId.val(), that.ui.$location_id.val()),
                data: JSON.stringify({rating: rating, review: review}),
                success: function () {
                    $('.loader').addClass('hidden');
                    $('.btn-review-submit').removeClass('hidden');
                    $('.rate-stars').rateYo('rating', 0);
                    $('.review').val('');
                    $('.rate-location-dialog').dialog('close');
                    window.location.reload();
                }
            });
        });
    },

    clickFavoriteIcon: function clickFavoriteIcon() {
        var that = this;
        $('.location-like').on('click', function () {
            var $el = $(this);
            if ($el.hasClass('active')) {
                that.favoriteLocation({like: false}, function () {
                    $el.addClass('favorite-icon');
                    $el.removeClass('fa fa-heart fa-2x');
                    $el.removeClass('heart-active');
                    $el.removeClass('active');
                });
            } else {
                that.favoriteLocation({like: true}, function () {
                    $el.removeClass('favorite-icon');
                    $el.addClass('fa fa-heart fa-2x');
                    $el.addClass('heart-active');
                    $el.addClass('active');
                });
            }
        });
    },

    favoriteLocation: function favoriteLocation(data, successCallback) {
        $.ajax({
            method: 'POST',
            url: this.urls.favorite.format(this.ui.$businessId.val(), this.ui.$location_id.val()),
            dataType: 'json',
            data: JSON.stringify(data),
            success: function () {
                if (successCallback) {
                    successCallback();
                }
            }
        });
    },

    clickPhoneNumberLink: function clickPhoneNumberLink() {
        var that = this;
        $('.phone-number').on('click', function (e) {
            // Fo mobile devices do not prevent 'tel:' default
            if ($(window).outerWidth() > 768) {
                e.preventDefault();
                that.showPhoneDialog();
            }
        });
    },

    showPhoneDialog: function showPhoneDialog() {
        W.common.Dialog($('.phone-dialog'), function () {
            $('.btn-close-phone-dialog').off('click');
        }, {height: 400, width: 370});

        $('.dialog-phone-message').text('Call: {0}'.format(this.location.phone));
        $('.btn-close-phone-dialog').on('click', function () {
            $('.phone-dialog').dialog('close');
        });

        W.track({
            event: "DISP_CALL",
            entity_id: this.ui.$businessId.val()
        })


    },

    clickPlaceOrderBtn: function clickPlaceOrderBtn() {
        var that = this,
            $btn = $('.btn-place-order');
        if ($btn && $btn.length !== 0) {
            $btn.on('click', function () {
                that.showPhoneDialog();
            });
        }
    },

    clickAvgPriceIndicator: function () {
        var $btn = $('.avg-price');

        if ($btn.length !== 0) {
            $btn.on('click', function () {
                W.common.Dialog($('.avg-price-dialog'), function () {}, {height: 200, width: 'auto'});
            });
        }
    },

    clickGetDirectionsBtn: function clickGetDirectionsBtn() {
        var that = this, $btn = $('.btn-get-directions'), q;
        if ($btn && $btn.length !== 0) {
            $btn.on('click', function () {
                q = W.common.Format.formatAddress(that.location);
                
                W.track({
                    event: "DISP_GETDIR",
                    entity_id: that.ui.$businessId.val()
                });

                if (q) {
                    setTimeout(function(){
                        window.open('http://maps.google.com/?daddr={0}?sadds='.format(q), '_blank');
                    }, 1200);
                    
                }
            });
        }
    },

    showContent: function showContent() {
        var that = this;
        $.when(this.getMenuItemsDeferred(), this.getReviewsDeferred())
            .done(function (menu_response, reviews_response) {
                that.menu_items = menu_response && menu_response[0];
                that.reviews = reviews_response && reviews_response[0]['reviews'];

                that.preFormatReviews();

                that.menu_sativas = that.getSortedMenuItems('sativa');
                that.menu_indicas = that.getSortedMenuItems('indica');
                that.menu_hybrids = that.getSortedMenuItems('hybrid');

                var reviews = _.map(that.reviews, _.clone),
                    reviewToShow = reviews.length > 2 ? reviews.splice(0, 2) : reviews;

                that.regions.$contentRegion.html(that.templates.$content({
                    l: that.location,
                    sativas: that.menu_sativas,
                    indicas: that.menu_indicas,
                    hybrids: that.menu_hybrids,
                    selectedVtMenuItem: that.selectedVtMenuItem,
                    formatPrice: that.formatPrice,
                    formatScore: that.formatScore,
                    getVtUrl: that.getVtUrl,
                    reviews: reviewToShow,
                    deals: [],
                    is_authenticated: AUTHENTICATED
                }));

                that.postShowContent();
            });
    },

    postShowContent: function postShowContent() {
        var that = this;
        $.each($('.review-wrapper'), function () {
            var $el = $(this),
                $rating = $el.find('.rating'),
                $review = $el.find('.display-text');

            W.common.Rating.readOnly($rating, {rating: $rating.text()});
            that.changeReviewText($review);
        });

        this.expandReviewText();
        this.showAllReviews();

        $('.btn-request').on('click', this.onBtnRequestClick.bind(this));
        $('.menu-item-header .match').on('click', this.showMatchInfoDialog.bind(this));
        $('.out-of-stock')
            .on('click', this.showOutOfStockDialog.bind(this));
    },

    postUpdateRequest: function postUpdateRequest(url) {
        var message = $.trim($('#request-message').val()),
            notify = $('#request-notify').is(':checked');

        var payload = {};
        if (message) {
            payload.message = message;
        }

        if (notify) {
            payload.send_notification = notify;
        }

        return $.ajax({
            method: 'POST',
            url: url,
            dataType: 'json',
            data: JSON.stringify(payload)
        });
    },

    login: function login() {
        var email = $('#login').val(),
            password = $('#password').val(),
            that = this;

        return $.ajax({
            method: 'POST',
            url: '/api/v1/users/login',
            dataType: 'json',
            data: JSON.stringify({ email: email, password: password }),
            success: function (data) {
                var user = data.user;
                if (user) {
                    W.common.ActionRecorder.identify(user.id);
                    W.common.ActionRecorder.peopleSet({
                        '$first_name': user.first_name,
                        '$last_name': user.last_name,
                        '$last_login': new Date(),
                        '$email': user.email,
                        'account_type': user.type
                    });

                    that.user.firstName = user.first_name;

                    if (user.geo_location) {
                        that.user.city = user.geo_location.city;
                    }
                }
                W.pages.Common.ajaxSetup();

                that.isAuthorized = true;
                that.showMenuUpdateRequestDialog();
            },
            error: function (error) {
                if (error.status === 400) {
                    $('#menu-update-request-login-dialog .error-message').text(JSON.parse(error.responseText).error);
                }
            }
        });

    },

    changeReviewText: function changeReviewText($review) {
        var reviewHeight = $review.height(),
            reviewText = $review.text(),
            fontSize = parseInt($review.css('font-size'), 10);

        if (reviewHeight / fontSize >= 2) {
            reviewText = reviewText.substr(0, 65) + '... <span class="expander">Review full review</span>';
            $review.html(reviewText);
        }
    },

    expandReviewText: function expandReviewText() {
        $('.expander').on('click', function () {
            var parent = $(this).parent().parent();
            parent.find('.display').addClass('hidden');
            parent.find('.full').removeClass('hidden');
        });
    },

    showAllReviews: function showAllReviews() {
        var that = this;

        $('.all-reviews-link-wrapper a').on('click', function (e) {
            e.preventDefault();

            var reviews = _.map(that.reviews, _.clone),
                reviewToShow = reviews.length > that.allReviewsSize ? reviews.splice(0, that.allReviewsSize) : reviews;

            that.regions.$contentRegion.html(that.templates.$allReviews({
                showNext: that.reviews.length > that.allReviewsSize,
                showPrev: that.allReviewsPage > 1,
                reviews: reviewToShow
            }));

            $.each($('.review-wrapper'), function () {
                var $el = $(this), $rating = $el.find('.rating');
                W.common.Rating.readOnly($rating, {rating: $rating.text()});
            });

            that.initAllReviewsControls();
        });
    },

    initAllReviewsControls: function initAllReviewsControls() {
        var that = this;

        $('.btn-back').on('click', function (e) {
            e.preventDefault();

            var reviews = _.map(that.reviews, _.clone),
                reviewToShow = reviews.length > 2 ? reviews.splice(0, 2) : reviews;

            that.regions.$contentRegion.html(that.templates.$content({
                l: that.location,
                sativas: that.menu_sativas,
                indicas: that.menu_indicas,
                hybrids: that.menu_hybrids,
                selectedVtMenuItem: that.selectedVtMenuItem,
                formatPrice: that.formatPrice,
                formatScore: that.formatScore,
                reviews: reviewToShow,
                deals: []
            }));

            that.postShowContent();
        });

        $('.reviews-next').on('click', function (e) {
            e.preventDefault();

            var reviews = _.map(that.reviews, _.clone),
                reviewToShow = reviews.length > that.allReviewsSize ?
                    reviews.splice(that.allReviewsPage * that.allReviewsSize, that.allReviewsSize) : reviews;

            that.allReviewsPage += 1;

            that.regions.$contentRegion.html(that.templates.$allReviews({
                showNext: that.reviews.length > that.allReviewsSize * that.allReviewsPage,
                showPrev: that.allReviewsPage > 1,
                reviews: reviewToShow
            }));

            $.each($('.review-wrapper'), function () {
                var $el = $(this), $rating = $el.find('.rating');
                W.common.Rating.readOnly($rating, {rating: $rating.text()});
            });

            that.initAllReviewsControls();
        });

        $('.reviews-prev').on('click', function (e) {
            e.preventDefault();

            that.allReviewsPage -= 1;

            var reviews = _.map(that.reviews, _.clone),
                reviewToShow = reviews.length > that.allReviewsSize ?
                    reviews.splice((that.allReviewsPage - 1) * that.allReviewsSize, that.allReviewsSize) : reviews;


            that.regions.$contentRegion.html(that.templates.$allReviews({
                showNext: that.reviews.length > that.allReviewsSize,
                showPrev: that.allReviewsPage > 1,
                reviews: reviewToShow
            }));

            $.each($('.review-wrapper'), function () {
                var $el = $(this), $rating = $el.find('.rating');
                W.common.Rating.readOnly($rating, {rating: $rating.text()});
            });

            that.initAllReviewsControls();
        });
    },

    getMenuItemsDeferred: function getMenuItemsDeferred() {
        return $.ajax({
            method: 'GET',
            url: this.urls.menu.format(this.ui.$businessId.val(), this.ui.$location_id.val())
        });
    },

    getReviewsDeferred: function getReviewsDeferred() {
        return $.ajax({
            method: 'GET',
            url: this.urls.review.format(this.ui.$businessId.val(), this.ui.$location_id.val())
        });
    },

    preFormatReviews: function preFormatReviews() {
        if (this.reviews && this.reviews.length > 0) {
            $.each(this.reviews, function (i, r) {
                var date = new Date(r.created_date),
                    year = date.getFullYear() - 2000,
                    month = date.getMonth() + 1,
                    day = date.getDate();

                r.review = r.review ? r.review : '(No review written)';
                r.created_date = '{0}/{1}/{2}'.format(month, day, year);
            });
        }
    },

    getSortedMenuItems: function getSortedMenuItems(type) {
        if (this.menu_items && this.menu_items.length > 0) {
            var that = this,
                vtId = parseInt(this.ui.$vt_id.val(), 10),
                filtered = _.filter(this.menu_items, function (item) {
                    if (parseInt(item.vt_id, 10) === vtId) {
                        that.selectedVtMenuItem = item;
                    }

                    if (item.vt_variety === type) {
                        return item;
                    }
                });
            filtered.sort(this.sortMenuItems);
            return filtered;
        }

        return [];
    },

    sortMenuItems: function sortMenuItems(el1, el2) {
        var aScore = el1.match_score, bScore = el2.match_score;
        return aScore < bScore ? 1 : aScore > bScore ? -1 : 0;
    },

    formatPrice: function formatPrice(price) {
        return price ? '${0}'.format(price) : '--';
    },

    formatScore: function formatScore(score) {
        return score ? '{0}%'.format(score) : '--';
    },

    closeDialog: function closeDialog() {
        if (this.dialog) {
            this.dialog.dialog('close');
        }
    },

    onBtnRequestClick: function onBtnRequestClick() {
        if (this.isAuthenticated) {
            this.showMenuUpdateRequestDialog()
        } else {
            this.showMenuUpdateRequestLoginDialog();
        }

    },

    showMenuUpdateRequestDialog: function showMenuUpdateRequestDialog() {
        var url = this.urls.menuUpdateRequest.format(this.ui.$businessId.val(), this.ui.$location_id.val()),
            that = this,
            $dialogBtn = $('#menu-update-request-dialog .btn-request-update'),
            $requestBtn = $('.btn-request');

        that.closeDialog();
        $dialogBtn.text('Request an Update');

        that.dialog = MenuUpdateRequestDialog(that.user, that.location, function() {
            $dialogBtn.attr('disabled', true);
            $dialogBtn.text('Sending Request ...');

            that.postUpdateRequest(url).always(function() {
                $requestBtn.attr('disabled', true);
                $requestBtn.attr('title', 'You have recently requested a menu update');

                that.showMenuUpdateRequestOkDialog();
            });
        });
    },

    showOutOfStockDialog: function (event) {
        if (!this.isAuthenticated) {
            return false;
        }
        var $requestBtn = $(event.target).parents('.out-of-stock'),
            url = this.urls.reportOutOfStock.format(this.ui.$businessId.val(), $requestBtn.attr('data-menu-id')),
            that = this;

        that.closeDialog();
        that.dialog = Dialog('#out-of-stock-dialog', '#btn-report-out-of-stock', {title: 'Report out of stock'}, function () {
            that.postUpdateRequest(url).always(function() {
                $requestBtn.attr('disabled', true);
                $requestBtn.attr('title', 'You have recently report dispensary');
                that.showOutOfStockOkDialog();
            });
        }, '.cancel');
    },

    showOutOfStockOkDialog: function showMenuUpdateRequestOkDialog() {
        this.closeDialog();
        this.dialog = Dialog('#menu-update-request-ok-dialog', '#menu-update-request-ok-dialog #btn-close',
            {title: 'Report out of stock'}, this.closeDialog.bind(this));
    },

    showMenuUpdateRequestOkDialog: function showMenuUpdateRequestOkDialog() {
        this.closeDialog();
        this.dialog = MenuUpdateRequestOkDialog(this.closeDialog.bind(this));
    },

    showMenuUpdateRequestLoginDialog: function showMenuUpdateRequestLoginDialog() {
        this.closeDialog();
        this.dialog = MenuUpdateRequestLoginDialog(this.login.bind(this));
    },

    showMatchInfoDialog: function showMatchInfoDialog() {
        this.closeDialog();
        this.dialog = MatchInfoDialog();
    }

});


var Dialog = function Dialog(dialogSelector, btnSelector, props, onConfirm, btnCancel) {
    var $dialog = $(dialogSelector),
        width = 'auto',
        defaultProps;

    if ($(window).width() > 450) {
        width = '450px';
    }

    $dialog.removeClass('hidden');

    defaultProps = {
        classes: {
            'ui-dialog': 'menu-update-request-dialog srx-dialog'
        },
        closeOnEscape: true,
        height: 'auto',
        width: width,
        modal: true,
        draggable: false,
        resizable: false,
        title: 'Menu update request',
        position: {'my': 'center'},
        create: function () {
            $(this).css('max-width', '450px');
            $(this).css('min-height', 'auto');
            $('.srx-dialog').css('min-height', 'auto');
        }
    };

    $dialog.dialog($.extend(defaultProps, props));

    $(btnSelector).off('click');
    $(btnSelector).on('click', onConfirm);
    if (btnCancel) {
        $dialog.find(btnCancel)
            .off('click')
            .on('click', function () {
                $dialog.dialog('close');
            });
    }
    $(':focus').blur();
    $dialog.focus();

    return $dialog;
};


var MenuUpdateRequestDialog = function MenuUpdateRequestDialog(user ,location, onConfirm) {
    var dialog = Dialog('#menu-update-request-dialog', '#btn-request-update', {}, onConfirm);
    var defaultMessage = [];
    if (user.city) {
        defaultMessage.push('From {0} in {1}:'.format(user.firstName, user.city));
    } else {
        defaultMessage.push('From {0}:'.format(user.firstName));
    }

    defaultMessage = defaultMessage.concat([
        '',
        location.location_name + ',',
        'Please update your Vt menu.',
        'Thank you!'

    ]);

    $('#menu-update-request-dialog textarea').val(defaultMessage.join('\n'));

    return dialog;
};


var MenuUpdateRequestOkDialog = function MenuUpdateRequestOkDialog(onConfirm) {
    return Dialog('#menu-update-request-ok-dialog', '#btn-close', {}, onConfirm);
};


var MenuUpdateRequestLoginDialog = function MenuUpdateRequestOkDialog(onConfirm) {
    return Dialog('#menu-update-request-login-dialog', '#btn-sign-in', {}, onConfirm);
};


var MatchInfoDialog = function MatchInfoDialog() {
    return Dialog('#match-info-dialog', '', { classes: {}, title: 'Match %' });
};
