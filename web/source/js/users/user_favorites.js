'use strict';

W.ns('W.users');

W.users.FavoritesPage = Class.extend({

    ui: {
        $userId: $('.user-id')
    },

    regions: {
        $favorites: $('.user-favorites')
    },

    subTabs: {
        $vts: $('.vts-tab'),
        $dispensaries: $('.dispensaries-tab'),
        $deliveries: $('.deliveries-tab')
    },

    urls: {
        favorites: '/api/v1/users/{0}/favorites/{1}/',
        delete: '/api/v1/users/{0}/favorites/{1}/{2}'
    },

    init: function () {
        var that = this;
        this.retrieveVtFavorites(function (favorites) {
            that.renderVtFavorites(favorites);
            that.removeFavorite();
        });
        this.initSubTabs();
    },

    retrieveVtFavorites: function retrieveVtFavorites(success) {
        var that = this;
        $.ajax({
            method: 'GET',
            url: this.urls.favorites.format(that.ui.$userId.val(), 'vt'),
            success: function (data) {
                success(data);
            }
        });
    },

    retrieveDispensariesFavorites: function retrieveDispensariesFavorites(success) {
        var that = this;
        $.ajax({
            method: 'GET',
            url: this.urls.favorites.format(that.ui.$userId.val(), 'dispensary'),
            success: function (data) {
                success(data);
            }
        });
    },

    retrieveDeliveriesFavorites: function retrieveDeliveriesFavorites(success) {
        var that = this;
        $.ajax({
            method: 'GET',
            url: this.urls.favorites.format(that.ui.$userId.val(), 'delivery'),
            success: function (data) {
                success(data);
            }
        });
    },

    renderVtFavorites: function renderVtFavorites(favorites) {
        var that = this,
            template = _.template($('#user_favorite_vt_template').html());

        this.regions.$favorites.html('');

        if (favorites && favorites.length === 0) {
            this.regions.$favorites.html('No favorite vts');
        }

        $.each(favorites, function (index, favorite) {
            that.preformatFavorite(favorite);
            that.regions.$favorites.append(template({'favorite': favorite}));
            that.initRating($('.overall-rating-{0}'.format(favorite.id)), favorite.vt_overall_rating);
        });
    },

    initRating: function initRating($ratingSelector, rating) {
        if (rating !== 'Not Rated') {
            W.common.Rating.readOnly($ratingSelector, {rating: rating});
        }
    },

    removeFavorite: function removeFavorite() {
        var that = this;
        $('.favorite').on('click', '.removable', function () {
            var $this = $(this);

            $.ajax({
                method: 'DELETE',
                url: that.urls.delete.format(that.ui.$userId.val(), $this.attr('data-type'), $this.prop('id')),
                success: function () {
                    $this.parents('.favorite').remove();
                }
            });
        });
    },

    renderDispensariesFavorites: function renderDispensariesFavorites(favorites, delivery) {
        var that = this,
            template = _.template($('#user_favorite_dispensary_template').html());

        this.regions.$favorites.html('');

        if (favorites && favorites.length === 0) {
            if (delivery){
                this.regions.$favorites.html('No Dispensaries Added');
            } else {
                this.regions.$favorites.html('No Deliveries Added');
            }
        }

        $.each(favorites, function (index, favorite) {
            that.preformatFavorite(favorite);
            that.regions.$favorites.append(template({'favorite': favorite}));
            that.initRating($('.overall-rating-{0}'.format(favorite.id)), favorite.vt_overall_rating);
        });
    },

    preformatFavorite: function preformatFavorite(review) {
        var date = new Date(review.created_date),
            year = date.getFullYear() - 2000,
            month = date.getMonth() + 1,
            day = date.getDate();

        review.created_date = '{0}/{1}/{2}'.format(month, day, year);
    },

    initSubTabs: function initSubTabs() {
        var that = this;

        this.subTabs.$vts.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveVtFavorites(function (favorites) {
                that.renderVtFavorites(favorites);
                that.removeFavorite();
            });
        });

        this.subTabs.$dispensaries.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveDispensariesFavorites(function (favorites) {
                that.renderDispensariesFavorites(favorites);
                that.removeFavorite();
            });
        });

        this.subTabs.$deliveries.on('click', function () {
            $('.sub-tab').removeClass('active');
            $(this).addClass('active');
            that.retrieveDeliveriesFavorites(function (favorites) {
                that.renderDispensariesFavorites(favorites, true);
                that.removeFavorite();
            });
        });
    }

});
