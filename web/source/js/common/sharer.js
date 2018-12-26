'use strict';

W.ns('W.common');

W.common.Sharer = {

    getSharerUrls: function getSharerUrls(urlToShare) {
        var urls = W.common.Constants.sharerUrls;
        return {
            facebook: urls.facebook.format(urlToShare),
            google: urls.google.format(urlToShare),
            twitter: urls.twitter.format(urlToShare)
        }
    }

};
