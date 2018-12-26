'use strict';

W.ns('W.pages.search.vt');

W.pages.search.vt.SearchView = function () {

    var Model = W.common.Model,
        SearchWizard = W.pages.search.vt.SearchWizard;

    return {
        init: function () {
            new SearchWizard({
                model: new Model()
            });
        }
    };
}();
