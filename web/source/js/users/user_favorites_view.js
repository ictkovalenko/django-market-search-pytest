'use strict';

W.ns('W.users');

W.users.FavoritesView = function () {

    var FavoritesPage = W.users.FavoritesPage;

    return {
        init: function () {
            new FavoritesPage();
        }
    };
}();
