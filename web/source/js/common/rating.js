'use strict';

W.ns('W.common');

W.common.Rating = {

    readOnly: function readOnly($el, options) {
        if (options && options.rating) {
            $el.rateYo({
                rating: parseFloat(options.rating),
                readOnly: true,
                spacing: options.spacing || '1px',
                normalFill: '#aaa8a8', // $grey-light
                ratedFill: '#6bc331', // $avocado-green
                starWidth: options.starWidth || '16px',
                starSvg: options.starSvg || null
            });
        }
    }

};
