'use strict';

W.ns('W.common');

W.common.Constants = {

    html: {
        loader: '<i class="fa fa-spinner fa-pulse" aria-hidden="true"></i>'
    },

    regex: {
        email: /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
        phone: /^[0-9]{3}-[0-9]{3}-[0-9]{4}$/,
        specialChar: /[~`!@#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?]/,
        onlyNumeric: /^\d+$/,
        onlyAlpha: /^[a-zA-Z\s]+$/
    },

    masks: {
        phone: {
            mask: '000-000-0000',
            placeholder: '___-___-____'
        },
        time: {
            mask: '00:00',
            placeholder: 'hh:mm'
        }
    },

    days: [
        {name: 'Monday', value: 'mon'},
        {name: 'Tuesday', value: 'tue'},
        {name: 'Wednesday', value: 'wed'},
        {name: 'Thursday', value: 'thu'},
        {name: 'Friday', value: 'fri'},
        {name: 'Saturday', value: 'sat'},
        {name: 'Sunday', value: 'sun'}
    ],

    sharerUrls: {
        facebook: 'https://www.facebook.com/sharer/sharer.php?u={0}',
        google: 'https://plus.google.com/share?url={0}',
        twitter: 'https://twitter.com/home?status={0}'
    },

    effectNames: {
        'happy': 'Happy',
        'uplifted': 'Uplifted',
        'stimulated': 'Stimulated',
        'energetic': 'Energetic',
        'creative': 'Creative',
        'focused': 'Focused',
        'relaxed': 'Relaxed',
        'sleepy': 'Sleepy',
        'talkative': 'Talkative',
        'euphoric': 'Euphoric',
        'hungry': 'Hungry',
        'tingly': 'Tingly',
        'good_humored': 'Good Humored'
    },

    benefitNames: {
        'reduce_stress': 'Reduce Stress',
        'help_depression': 'Help Depression',
        'relieve_pain': 'Relieve Pain',
        'reduce_fatigue': 'Reduce Fatigue',
        'reduce_headaches': 'Reduce Headaches',
        'help_muscles_spasms': 'Help Muscles Spasms',
        'lower_eye_pressure': 'Lower Eye Pressure',
        'reduce_nausea': 'Reduce Nausea',
        'reduce_inflammation': 'Reduce Inflammation',
        'relieve_cramps': 'Relieve Cramps',
        'help_with_seizures': 'Help With Seizures',
        'restore_appetite': 'Restore Appetite',
        'help_with_insomnia': 'Help With Insomnia'
    },

    sideEffectNames: {
        'anxiety': 'Anxiety',
        'dry_mouth': 'Dry Mouth',
        'paranoia': 'Paranoia',
        'headache': 'Headache',
        'dizziness': 'Dizziness',
        'dry_eyes': 'Dry Eyes',
        'spacey': 'Spacey',
        'lazy': 'Lazy',
        'hungry': 'Hungry',
        'groggy': 'Groggy'
    },

    VtVarieties: {
        indica: 'Indica',
        sativa: 'Sativa',
        hybrid: 'Hybrid'
    }

};
