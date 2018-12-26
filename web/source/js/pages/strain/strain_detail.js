'use strict';

W.ns('W.pages.vt');

W.pages.vt.VtDetailPage = Class.extend({

    effectNames: W.common.Constants.effectNames,
    benefitNames: W.common.Constants.benefitNames,
    sideEffectNames: W.common.Constants.sideEffectNames,

    flavorsData: [],
    images: [],

    ui: {
        $vtId: $('.vt-id'),
        $locationControl: '.location-controls'
    },

    urls: {
        locationAutocomplete: '/api/v1/businesses/location/lookup/'
    },

    templates: {
        expandedLocation: _.template($('#vt_detail_available_location').html())
    },

    priceSort: 'asc',
    locationBlocked: undefined,

    init: function init(options) {
        var that = this;
        this.name = 'VtDetailPage';
        this.authenticated = options.authenticated || false;

        that.retrieveFlavors(function (flavors) {
            that.flavorsData = flavors;
            that.retrieveVt(function (vt_data) {
                if (vt_data) {
                    var qs = W.qs(),
                        search = qs['search'],
                        allowedLetters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
                        firstLetter;

                    that.model = new W.common.Model(vt_data);
                    that.model.set('from_search', search);
                    that.model.set('from_advanced_search', window.location.search);
                    that.model.set('share_urls', W.common.Sharer.getSharerUrls(encodeURIComponent(window.location.href)));

                    firstLetter = that.model.get('vt').name.charAt(0).toLowerCase();
                    firstLetter = allowedLetters.indexOf(firstLetter) > -1 ? firstLetter : 'other';

                    that.model.get('vt').first_letter = firstLetter === 'other' ? 'Other' : firstLetter.toUpperCase();
                    that.model.get('vt').first_letter_esc = firstLetter;

                    that.preformatModel();
                    that.renderVtDetails();
                }
            });
        });
        that.checkGeolocationPermission();

        W.subscribe.apply(this);
    },

    _on_close_popup: function _on_close_popup() {
        $('.locations').addClass('hidden');
        $('.filter-menu').removeClass('expanded');
    },

    retrieveFlavors: function retrieveFlavors(success) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/flavors',
            success: function (data) {
                success(data);
            }
        });
    },

    retrieveVt: function retrieveVt(success) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/vt/{0}/details'.format(this.ui.$vtId.val()),
            success: function (data) {
                success(data);
            }
        });
    },

    preformatModel: function preformatModel() {
        if (this.model.get('vt_reviews')) {
            $.each(this.model.get('vt_reviews'), function (index, review) {
                var date = new Date(review.created_date),
                    year = date.getFullYear() - 2000,
                    month = date.getMonth() + 1,
                    day = date.getDate();

                review.review = review.review ? review.review : '(No review written)';
                review.created_date = '{0}/{1}/{2}'.format(month, day, year);
            });
        }
    },

    checkGeolocationPermission: function handlePermission(success) {
        var that  = this;
        if (this.authenticated) {
            that.locationBlocked = false;
            if (success) {
                success()
            }
            return;
        }

        navigator.permissions.query({name: 'geolocation'}).then(function (result) {
            if (result.state === 'granted') {
                that.locationBlocked = false
            } else if (result.state === 'prompt' || result.state === 'denied') {
                that.locationBlocked = true
            }

            if (success) {
                success()
            }
        });
    },

    renderVtDetails: function renderVtDetails() {
        var template = _.template($('#vt_details_page').html());

        $('.vt-detail-wrapper').append(template({
            'model': this.model.getData(),
            'abbreviateVtName': abbreviateVtName,
            'is_authenticated': AUTHENTICATED
        }));

        function abbreviateVtName(vtName) {
            var words = vtName.split(' '),
                abbreviation = '';

            if (words && words.length === 1) {
                abbreviation = words[0].substr(0, 2);
            } else {
                for (var i = 0; i < words.length; i++) {
                    abbreviation += words[i].substr(0, 1).toUpperCase();
                }
            }

            return abbreviation;
        }

        this.retrieveAndRenderAlsoLikeVts();
        this.retrieveAndRenderImages();

        this.populateEffects();
        this.populateBenefits();
        this.populateSideEffects();
        this.populateFlavors();

        this.initRatings();
        this.vtFavoriteHover();
        this.vtFavoriteClick();

        this.uploadPhotoListener();
        this.buildLocationsMenu();
        this.showRateVtDialog();
        this.addReviewMention();
        this.submitVtReview();
        this.showAllReviews();

        new W.pages.vt.VtReviewDialog({
            model: this.model
        });
    },

    retrieveAndRenderAlsoLikeVts: function retrieveAndRenderAlsoLikeVts() {
        var $alsoLikeWrapper = $('.similar-vts-wrapper');
        $alsoLikeWrapper.html(W.common.Constants.html.loader);

        $.ajax({
            method: 'GET',
            url: '/api/v1/search/vt/{0}/also_like'.format($('.vt-id').val()),
            success: function (data) {
                if (data.also_like_vts.length > 0) {
                    var template = _.template($('#vt_detail_also_like_template').html());
                    $alsoLikeWrapper.html('');
                    $.each(data.also_like_vts, function (i, s) {
                        $alsoLikeWrapper.append(template({s: s}));
                    });
                } else {
                    $alsoLikeWrapper.text('None');
                    $alsoLikeWrapper.css('margin-top', '1em');
                }

                setTimeout(function () {
                    $(window).trigger('resize');
                }, 500);
            }
        });

        // 500 ms to hide a default ajax loader spinner
        setTimeout(function () {
            $('#loading-spinner').hide();
        }, 500);
    },

    retrieveAndRenderImages: function retrieveAndRenderImages() {
        var that = this,
            $loader = $('.vt-photo-wrapper .loader');

        $loader.html(W.common.Constants.html.loader);

        $.ajax({
            method: 'GET',
            url: '/api/v1/search/vt/{0}/images/'.format($('.vt-id').val()),
            success: function (data) {
                $loader.html('');

                if (data && data.images && data.images.length > 0) {
                    that.images = data.images;
                } else {
                    $('.vt-photo-wrapper .main-image img').removeClass('hidden');
                }

                that.populateImages();
            }
        });

        // 500 ms to hide a default ajax loader spinner
        setTimeout(function () {
            $('#loading-spinner').hide();
        }, 500);
    },

    populateImages: function populateImages() {
        var $imageCarousel = $('.image-carousel'),
            $mainImage = $('.vt-photo-wrapper .main-image'),
            $mainImageImg = $mainImage.find('img'),
            $carouselImageWrapper = $('.carousel-images-wrapper'),
            imgWrapperTemplate = '<div class="img-wrapper"><img src="{0}"/><div class="cover"></div></div>',
            firstImage = $mainImageImg.attr('src'),
            $cover,
            that = this;

        $imageCarousel.removeClass('hidden');

        $.each(this.images, function (index, img) {
            $carouselImageWrapper.append(imgWrapperTemplate.format(img.image));
        });

        if (this.images.length < 5) {
            for (var j = 0; j < 5 - this.images.length; j++) {
                $carouselImageWrapper.append(imgWrapperTemplate.format(firstImage));
            }

            $('.carousel-arrow').addClass('hidden');
        }

        if ($(document).width() < 440 || this.images.length <= 5) {
            $('.carousel-arrow.arrow-left, .carousel-arrow.arrow-right').removeClass('hidden');
        }

        if (this.images.length > 0) {
            firstImage = this.images[0].image;
        }

        $cover = $('.cover');
        $cover.first().addClass('active');
        $cover.on('click', function () {
            var $el = $(this);
            $cover.removeClass('active');
            $mainImageImg.attr('src', $el.parent().find('img').attr('src'));
            $el.addClass('active');
        });

        $mainImageImg.attr('src', firstImage);
        $mainImageImg.removeClass('hidden');

        $('.arrow-up').on('click', function (e) {
            $carouselImageWrapper.scrollTop($carouselImageWrapper.scrollTop() - $('.img-wrapper').height());
        });

        $('.arrow-down').on('click', function (e) {
            $carouselImageWrapper.scrollTop($carouselImageWrapper.scrollTop() + $('.img-wrapper').height());
        });

        $('.arrow-left').on('click', function (e) {
            $carouselImageWrapper.scrollLeft($carouselImageWrapper.scrollLeft() - $('.img-wrapper').width());

        });

        $('.arrow-right').on('click', function (e) {
            $carouselImageWrapper.scrollLeft($carouselImageWrapper.scrollLeft() + $('.img-wrapper').width());
        });
    },

    initRatings: function initRatings() {
        var that = this,
            $vtRatingStars = $('.vt-rating-stars'),
            value = $vtRatingStars.text();

        this.initRating($vtRatingStars, value);
        $.each(this.model.get('vt_reviews'), function (index, review) {
            that.initRating($('.rating-{0}'.format(review.id)), review.rating);
            that.changeReviewText($('.display-text-{0}'.format(review.id)));
        });
        this.expandReviewText();
    },

    initRating: function initRating($ratingSelector, rating) {
        W.common.Rating.readOnly($ratingSelector, {rating: rating !== 'Not Rated' ? rating : 0});
    },

    changeReviewText: function changeReviewText($review) {},

    expandReviewText: function expandReviewText() {
        $('.expander').on('click', function () {
            var parent = $(this).parent().parent();
            parent.find('.display').addClass('hidden');
            parent.find('.full').removeClass('hidden');
        });
    },

    vtFavoriteHover: function vtFavoriteHover() {
        var $vtLike = $('.vt-like');

        $vtLike.mouseenter(function () {
            var $el = $(this);
            if (!$el.hasClass('active')) {
                $el.removeClass('favorite-icon');
                $el.addClass('fa fa-heart fa-2x');
                $el.addClass('heart-active');
            }
        });

        $vtLike.mouseleave(function () {
            var $el = $(this);
            if (!$el.hasClass('active')) {
                $el.addClass('favorite-icon');
                $el.removeClass('fa fa-heart fa-2x');
                $el.removeClass('heart-active');
            }
        });
    },

    vtFavoriteClick: function vtFavoriteClick() {
        var that = this,
            $vtLike = $('.vt-like');

        $vtLike.on('click', function () {
            var $el = $(this);
            if ($el.hasClass('active')) {
                that.likeVt({
                    like: false
                }, function () {
                    $el.addClass('favorite-icon');
                    $el.removeClass('fa fa-heart fa-2x');
                    $el.removeClass('heart-active');
                    $el.removeClass('active');
                });
            } else {
                that.likeVt({
                    like: true
                }, function () {
                    $el.removeClass('favorite-icon');
                    $el.addClass('fa fa-heart fa-2x');
                    $el.addClass('heart-active');
                    $el.addClass('active');
                });
            }
        });
    },

    likeVt: function likeVt(data, successCallback) {
        var that = this;
        $.ajax({
            method: 'POST',
            url: '/api/v1/search/vt/{0}/favorite'.format(that.ui.$vtId.val()),
            dataType: 'json',
            data: JSON.stringify(data),
            success: function () {
                if (successCallback) {
                    successCallback();
                }
            }
        });
    },

    buildEffectsToDisplay: function buildEffectsToDisplay(rawEffects, userCriteria, effectNames) {
        var effectsToDisplay = [];
        $.each(rawEffects, function (name, value) {
            if (value > 0) {
                var userCriteriaValue = 0, criteriaEffect = [];
                if (userCriteria && userCriteria !== 'skipped') {
                    criteriaEffect = _.filter(userCriteria, function (o) {
                        return name === o.name;
                    });

                    if (criteriaEffect.length > 0) {
                        userCriteriaValue = criteriaEffect[0].value;
                    }
                }

                effectsToDisplay.push({
                    name: effectNames[name],
                    value: value,
                    userCriteriaValue: userCriteriaValue,
                    initialName: name
                });
            }
        });
        effectsToDisplay.sort(this.sortValues);
        return effectsToDisplay;
    },

    populateEffects: function populateEffects() {
        var that = this,
            review = this.model.get('user_vt_review'),
            userCriteria = this.model.get('user_criteria') || {},
            effects = review ? review.effects : this.model.get('vt').effects,
            toDisplay = this.buildEffectsToDisplay(effects, userCriteria.effects, this.effectNames),
            missingVtEffects = [];

        if (userCriteria && userCriteria.effects && userCriteria.effects !== 'skipped') {
            $.each(userCriteria.effects, function (i, e) {
                var existsInVt = _.filter(toDisplay, function (vtEffect) {
                    return vtEffect.initialName === e.name;
                });

                if (existsInVt.length === 0) {
                    missingVtEffects.push(e);
                }
            });
        }

        if (missingVtEffects.length > 0) {
            $.each(missingVtEffects, function (i, e) {
                if (e.value > 0) {
                    toDisplay.push({
                        name: that.effectNames[e.name],
                        value: e.value,
                        userCriteriaValue: e.value,
                        initialName: e.name,
                        missing: true
                    });
                }
            })
        }

        $('.effects-region').append(this.effectHtml(toDisplay));
    },

    populateBenefits: function populateBenefits() {
        var that = this,
            review = this.model.get('user_vt_review'),
            userCriteria = this.model.get('user_criteria') || {},
            effects = review ? review.benefits : this.model.get('vt').benefits,
            toDisplay = this.buildEffectsToDisplay(effects, userCriteria.benefits, this.benefitNames),
            missingVtBenefits = [];

        if (userCriteria && userCriteria.benefits && userCriteria.benefits !== 'skipped') {
            $.each(userCriteria.benefits, function (i, e) {
                var existsInVt = _.filter(toDisplay, function (vtEffect) {
                    return vtEffect.initialName === e.name;
                });

                if (existsInVt.length === 0) {
                    missingVtBenefits.push(e);
                }
            });
        }

        if (missingVtBenefits.length > 0) {
            $.each(missingVtBenefits, function (i, e) {
                if (e.value > 0) {
                    toDisplay.push({
                        name: that.benefitNames[e.name],
                        value: e.value,
                        userCriteriaValue: e.value,
                        initialName: e.name,
                        missing: true
                    });
                }
            })
        }

        $('.benefits-region').append(this.effectHtml(toDisplay));
    },

    populateSideEffects: function populateSideEffects() {
        var that = this,
            review = this.model.get('user_vt_review'),
            userCriteria = this.model.get('user_criteria') || {},
            effects = review ? review.side_effects : this.model.get('vt').side_effects,
            toDisplay = this.buildEffectsToDisplay(effects, userCriteria.side_effects, this.sideEffectNames),
            missingVtSideEffects = [];

        if (userCriteria && userCriteria.side_effects && userCriteria.side_effects !== 'skipped') {
            $.each(userCriteria.side_effects, function (i, e) {
                var existsInVt = _.filter(toDisplay, function (vtEffect) {
                    return vtEffect.initialName === e.name;
                });

                if (existsInVt.length === 0) {
                    missingVtSideEffects.push(e);
                }
            });
        }

        if (missingVtSideEffects.length > 0) {
            $.each(missingVtSideEffects, function (i, e) {
                if (e.value > 0) {
                    toDisplay.push({
                        name: that.sideEffectNames[e.name],
                        value: e.value,
                        userCriteriaValue: e.value,
                        initialName: e.name,
                        missing: true
                    });
                }
            })
        }

        $('.side-effects-region').append(this.sideEffectHtml(toDisplay));
    },

    populateFlavors: function populateFlavors() {
        var that = this,
            flavorsToDisplay = [];

        $.each(this.model.get('vt').flavor, function (data_name, value) {
            if (value > 0) {
                var flavor = _.filter(that.flavorsData, function (f) {
                    return f.data_name === data_name;
                });

                if (flavor && flavor.length > 0) {
                    flavorsToDisplay.push({
                        name: flavor[0].display_name,
                        img: flavor[0].image ? '<img src="{0}"/>'.format(flavor[0].image) :
                            '<img src="{0}{1}"/>'.format(STATIC_URL, 'images/flavors/apple-512.png'),
                        value: value
                    });
                }
            }
        });

        flavorsToDisplay.sort(this.sortValues);
        $('.flavors-region').append(this.flavorsHtml(flavorsToDisplay));
    },

    sortValues: function sortValues(el1, el2) {
        var aName = el1.name, bName = el2.name,
            aValue = el1.value, bValue = el2.value;
        return aValue > bValue ? -1 : aValue < bValue ? 1 : aName < bName ? -1 : aName > bName ? 1 : 0;
    },

    effectHtml: function effectHtml(toDisplay) {
        var template = _.template($('#vt_effects').html());
        return template({
            'effects': toDisplay,
            'effectFillHtml': this.effectFillHtml,
            'userCriteriaFillHtml': this.userCriteriaFillHtml
        });
    },

    effectFillHtml: function effectFillHtml(effect) {
        var fillWidth = effect.value * 0.2 * 100, // 1 point should take 20% of parent width
            fillHtml = '<span class="{0}" style="width: {1}%"></span>';

        if (effect.missing) {
            fillHtml = fillHtml.format('', fillWidth);
        } else {
            fillHtml = fillHtml.format('fill', fillWidth);
        }

        return fillHtml;
    },

    userCriteriaFillHtml: function userCriteriaFillHtml(effect) {
        var fillWidth = (effect.userCriteriaValue >= 6 ? effect.userCriteriaValue - 5 : effect.userCriteriaValue) * 0.2 * 100, // 1 point should take 20% of parent width
            fillHtml = '<span class="{0}" style="{1}">{2}</span>',
            tearHtml = '<div class="tear"><span class="tear-value">{0}</span></div>'.format(effect.userCriteriaValue);

        if (fillWidth > 0) {
            if (effect.missing) {
                fillHtml = fillHtml.format('user-fill', 'width: {0}%'.format(fillWidth), tearHtml);
            } else {
                var vtValue = (effect.value >= 6 ? effect.value - 5 : effect.value) * 0.2 * 100;
                fillHtml = effect.userCriteriaValue > (effect.value >= 6 ? effect.value - 5 : effect.value) ?
                    fillHtml.format('user-fill', 'width: {0}%; left: {1}%'.format(fillWidth - vtValue, vtValue), tearHtml) :
                    fillHtml.format('user-fill', 'width: {0}%'.format(fillWidth), tearHtml);
            }
        } else {
            fillHtml = '';
        }

        return fillHtml;
    },

    sideEffectFillHtml: function sideEffectFillHtml(effect) {
        var fillWidth = (effect.value >= 6 ? effect.value - 5 : effect.value) * 0.2 * 100, // 1 point should take 20% of parent width
            fillHtml = '<span class="{0}" style="width: {1}%"></span>';

        if (effect.missing) {
            fillHtml = fillHtml.format('', fillWidth);
        } else {
            fillHtml = fillHtml.format('fill', fillWidth);
        }

        return fillHtml;
    },

    sideEffectHtml: function sideEffectHtml(toDisplay) {
        var template = _.template($('#vt_side_effects').html());
        return template({
            'effects': toDisplay,
            'sideEffectFillHtml': this.sideEffectFillHtml,
            'userCriteriaFillHtml': this.userCriteriaFillHtml
        });
    },

    flavorsHtml: function flavorsHtml(toDisplay) {
        var template = _.template($('#vt_flavors').html());
        return template({'flavors': toDisplay});
    },

    uploadPhotoListener: function uploadPhotoListener() {
        var that = this;

        $('.add-photo-link').on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.upload-image-dialog'), function () {
                that.closeUploadDialog();
            });
        });

        $('.image-upload-form').on('submit', function (e) {
            e.preventDefault();
            $('.loader').removeClass('hidden');
            $('.btn-upload-image-submit').addClass('hidden');

            var file = $('.upload-image')[0].files[0],
                formData = new FormData();

            formData.append('file', file);
            formData.append('name', file.name);

            $.ajax({
                type: 'POST',
                url: '/api/v1/search/vt/{0}/images/'.format(that.ui.$vtId.val()),
                enctype: 'multipart/form-data',
                data: formData,
                processData: false,
                contentType: false,
                success: function () {
                    $('.loader').addClass('hidden');
                    $('.btn-upload-image-submit').addClass('hidden');
                    $('.submitted-message').removeClass('hidden');

                    var $btn = $('.btn-close');
                    $btn.removeClass('hidden');
                    $btn.on('click', function () {
                        that.closeUploadDialog();
                    });
                }
            });
        });

        $('.upload-image').on('change', function (e) {
            e.preventDefault();
            var $el = $(this),
                preview = $('.preview-image'),
                file = $el[0].files[0],
                reader = new FileReader();

            reader.addEventListener('load', function () {
                $('.photo-camera-wrapper').addClass('hidden');
                $('.preview-image-wrapper').removeClass('hidden');
                $('.btn-upload-image-submit').removeAttr('disabled');
                $('label[for="image-file"]').addClass('hidden');
                preview[0].src = reader.result;
            }, false);

            if (file) {
                reader.readAsDataURL(file);
            }
        });
    },

    closeUploadDialog: function closeUploadDialog() {
        $('.btn-close').addClass('hidden');
        $('.image-upload-form').get(0).reset();
        $('.btn-upload-image-submit').removeClass('hidden').attr('disabled', 'disabled');
        $('.photo-camera-wrapper').removeClass('hidden');
        $('label[for="image-file"]').removeClass('hidden');
        $('.preview-image-wrapper').addClass('hidden');
        $('.submitted-message').addClass('hidden');
        $('.upload-image-dialog').dialog('close');
    },

    buildLocationsMenu: function buildLocationsMenu() {
        var that = this,
            $menuExpander = $('.active-link'),
            $menuLocations = $('.locations'),
            $menuFilter = $('.filter-menu'),
            menuTemplate = _.template($('#vt_detail_available_locations').html()),
            vtId = that.ui.$vtId.val(),
            fromSearch = !!that.model.get('from_search');

        $menuExpander.on('click', function () {
            $menuLocations.toggleClass('hidden');
            $menuFilter.toggleClass('expanded');
            that.checkGeolocationPermission(function () {
                that.getDispensaries(function (dispensaries) {
                    $menuLocations.html(menuTemplate({
                        dispensaries: dispensaries || [],
                        renderLocation: that.templates.expandedLocation,
                        formatDistance: that.formatDistance,
                        formatPrice: that.formatPrice,
                        vt_id: vtId,
                        from_search: fromSearch,
                        locationBlocked: that.locationBlocked
                    }));

                    $('.price-sort').on('click', function () {
                        $('.prices-wrapper').toggleClass('hidden');
                    });

                    $('.prices-wrapper').mouseleave(function () {
                        $(this).addClass('hidden');
                    });

                    $('.price').on('click', function () {
                        $('.prices-wrapper').addClass('hidden');
                        var priceType = $(this).attr('id');
                        that.sortByPrice(priceType, false);
                    });

                    $('.dispensary-rating').each(function () {
                        var $this = $(this);
                        if ($this.text() !== 'Not Rated') {
                            that.initLocationRating($this, $this.text());
                        }
                    });

                    if ((that.locations && that.locations.length) || that.locationBlocked) {
                        $(that.ui.$locationControl).removeClass('disabled')
                    }
                    that.initSortActions();
                });
            });
        });

        $menuExpander.trigger('click');
    },

    initLocationRating: function initLocationRating($el, rating) {
        W.common.Rating.readOnly($el, {rating: rating, starWidth: '0.75em'});
    },

    renderLocation: function renderLocation(location) {
        var that = this,
            fromSearch = !!that.model.get('from_search');
        return this.templates.expandedLocation({
            d: location,
            formatDistance: this.formatDistance,
            formatPrice: this.formatPrice,
            vt_id: that.ui.$vtId.val(),
            from_search: fromSearch
        });
    },

    getDispensaries: function getDispensaries(success) {
        var that = this;

        if (this.locations) {
            success(this.locations);
        } else if (this.locationBlocked) {
            success();
        } else {
            $.ajax({
                method: 'GET',
                url: '/api/v1/search/vt/{0}/deliveries?filter=all&order_field=distance&order_dir=asc'.format(this.ui.$vtId.val()),
                success: function (data) {
                    that.locations = data.locations;
                    success(data.locations);
                }
            });
        }
    },

    initSortActions: function initSortActions() {
        var that = this,
            $sort = $('.sort'),
            $priceSort = $('.price-expander');

        $sort.on('click', function () {
            var $this = $(this);
            that.sortBy($this, $this.attr('id'));
        });

        $priceSort.on('click', function () {
            that.sortByPrice($('.price-value.active').attr('id'), true);
        });
    },

    sortBy: function sortBy($sort, sortFieldName) {
        var that = this, newSort, url;

        this.changeSortArrow($sort);

        newSort = $sort.hasClass('fa-caret-up') ? 'desc' : 'asc';
        url = '/api/v1/search/vt/{0}/deliveries?filter={1}&order_field={2}&order_dir={3}'
            .format(this.ui.$vtId.val(), 'all', sortFieldName, newSort);

        $.ajax({
            method: 'GET',
            url: url,
            success: function (data) {
                if (data && data.locations) {
                    var $expandedHolder = $('.locations-area-body');
                    $expandedHolder.html('');

                    $.each(data.locations, function (i, l) {
                        $expandedHolder.append(that.renderLocation(l));
                    });

                    $.each($expandedHolder.find('.dispensary-rating'), function (i, el) {
                        var $ratingSelector = $(el),
                            rating = $ratingSelector.text();
                        that.initLocationRating($ratingSelector, rating !== 'Not Rated' ? rating : 0);
                    });

                    $.each($('.price'), function () {
                        var $el = $(this);
                        if ($el.attr('id') === sortFieldName) {
                            $el.trigger('click');
                        }
                    });
                }
            }
        });
    },

    sortByPrice: function sortByPrice(sortFieldName, changeOrder) {
        var that = this, url;

        if (changeOrder) {
            this.priceSort = this.priceSort === 'asc' ? 'desc' : 'asc';
        }

        url = '/api/v1/search/vt/{0}/deliveries?filter={1}&order_field={2}&order_dir={3}'
            .format(this.ui.$vtId.val(), 'all', sortFieldName, this.priceSort);

        $.ajax({
            method: 'GET',
            url: url,
            success: function (data) {
                if (data && data.locations) {
                    var $expandedHolder = $('.locations-area-body');
                    $expandedHolder.html('');

                    $.each(data.locations, function (i, l) {
                        $expandedHolder.append(that.renderLocation(l));
                    });

                    $.each($expandedHolder.find('.dispensary-rating'), function (i, el) {
                        var $ratingSelector = $(el),
                            rating = $ratingSelector.text();
                        that.initLocationRating($ratingSelector, rating !== 'Not Rated' ? rating : 0);
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

    changeSortArrow: function changeSortArrow($el) {
        if ($el.hasClass('fa-caret-down')) {
            $el.removeClass('fa-caret-down');
            $el.addClass('fa-caret-up');
        } else {
            $el.removeClass('fa-caret-up');
            $el.addClass('fa-caret-down');
        }
    },

    showRateVtDialog: function showRateVtDialog() {
        $('.rate-link').on('click', function (e) {
            e.preventDefault();
            W.common.RateDialog($('.rate-vt-dialog'));
        });
    },

    addReviewMention: function () {
      var that = this;
      $('textarea.mention').mentionsInput({
          elastic: false,
          minChars: 1,
          showAvatars: false,
          onDataRequest: function (mode, query, callback) {
            var self = this;
            $.ajax({
                method: 'GET',
                url: that.urls.locationAutocomplete + '?q={0}'.format(query),
                success: function (data) {
                    callback.call(self, data);
                }
            })
          }
      });
    },

    submitVtReview: function submitVtReview() {
        var that = this;
        $('.rate-vt-form').on('submit', function (e) {
            e.preventDefault();
            var rating = $('.rate-stars').rateYo('rating'),
                review;

            $('textarea.mention').mentionsInput('val', function(text) {
                review = text || '';

                if (rating === 0) {
                    $('.error-message').text('Rating is required');
                    return;
                }

                $('.loader').removeClass('hidden');
                $('.btn-review-submit').addClass('hidden');

                $.ajax({
                    type: 'POST',
                    url: '/api/v1/search/vt/{0}/rate'.format(that.ui.$vtId.val()),
                    data: JSON.stringify({rating: rating, review: review}),
                    success: function () {
                        $('.loader').addClass('hidden');
                        $('.btn-review-submit').removeClass('hidden');
                        $('.rate-stars').rateYo('rating', 0);
                        $('.review').val('');
                        $('.rate-vt-dialog').dialog('close');
                        window.location.reload();
                    }
                });
            });
        });
    },

    showAllReviews: function showAllReviews() {
        var that = this;
        $('.all-reviews-link-wrapper a').on('click', function (e) {
            e.preventDefault();
            $.ajax({
                method: 'GET',
                url: '/api/v1/search/vt/{0}/reviews'.format(that.ui.$vtId.val()),
                success: function (data) {
                    that.model.set('vt_reviews', data.reviews);
                    $('.all-reviews-link-wrapper').addClass('hidden');

                    var $reviewsRegion = $('.reviews-wrapper'),
                        reviewTemplate = _.template($('#vt_review_template').html());

                    $reviewsRegion.html('');
                    $.each(that.model.get('vt_reviews'), function (index, review) {
                        var date = new Date(review.created_date),
                            year = date.getFullYear() - 2000,
                            month = date.getMonth() + 1,
                            day = date.getDate();

                        review.review = review.review ? review.review : '(No review written)';
                        review.created_date = '{0}/{1}/{2}'.format(month, day, year);

                        $reviewsRegion.append(reviewTemplate({review: review}));
                        that.initRating($('.rating-{0}'.format(review.id)), review.rating);
                        that.changeReviewText($('.display-text-{0}'.format(review.id)));
                    });
                    that.expandReviewText();
                }
            });
        });
    },

    formatDistance: function formatDistance(d) {
        return d ? '({0}mi)'.format(Math.round(d * 100) / 100) : 'n/a';
    },

    formatPrice: function formatPrice(p) {
        return p ? '${0}'.format(p) : 'n/a';
    }
});
