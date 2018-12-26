'use strict';

W.ns('W.common');

W.common.Parser = {

    parseJson: function parseJson(data) {
        try {
            return JSON.parse(data);
        } catch (Exception) {
            console.log('Cannot parse a JSON: {0}'.format(data));
            return {};
        }
    }

};
