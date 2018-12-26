TYPES = {
    'vt': "vt",
    'vt_review': "vt_review",
    'vt_rating': "vt_rating",
    'business_location': "business_location"
}

vt_mapping = {
    "properties": {
        "id": {
            "type": "long",
            "index": "not_analyzed"
        },
        "name": {
            "type": "string",
            "index": "analyzed",
            "analyzer": "name_analyzer",
            "norms": {
                "enabled": False
            },
            "fields": {
                "raw": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "stemmed": {
                    "type": "string",
                    "analyzer": "snowball"
                },
                "exact": {
                    "type": "string",
                    "index": "analyzed",
                    "analyzer": "exact_name_analyzer",
                }
            }
        },
        "vt_slug": {
            "type": "string",
            "index": "no"
        },
        "variety": {"type": "string"},
        "category": {"type": "string"},
        "cannabinoids": {
            "properties": {
                "thc": {"type": "double"},
                "thca": {"type": "double"},
                "thcv": {"type": "double"},
                "cbd": {"type": "double"},
                "cbg": {"type": "double"},
                "cbn": {"type": "double"},
                "cbc": {"type": "double"},
                "cbda": {"type": "double"},
            }
        },
        "effects": {
            "properties": {
                "happy": {"type": "short"},
                "uplifted": {"type": "short"},
                "stimulated": {"type": "short"},
                "energetic": {"type": "short"},
                "creative": {"type": "short"},
                "focused": {"type": "short"},
                "relaxed": {"type": "short"},
                "sleepy": {"type": "short"},
                "talkative": {"type": "short"},
                "euphoric": {"type": "short"},
                "hungry": {"type": "short"},
                "tingly": {"type": "short"},
                "good_humored": {"type": "short"}
            }
        },
        "benefits": {
            "properties": {
                "reduce_stress": {"type": "short"},
                "help_depression": {"type": "short"},
                "relieve_pain": {"type": "short"},
                "reduce_fatigue": {"type": "short"},
                "reduce_headaches": {"type": "short"},
                "help_muscles_spasms": {"type": "short"},
                "lower_eye_pressure": {"type": "short"},
                "reduce_nausea": {"type": "short"},
                "reduce_inflammation": {"type": "short"},
                "relieve_cramps": {"type": "short"},
                "help_with_seizures": {"type": "short"},
                "restore_appetite": {"type": "short"},
                "help_with_insomnia": {"type": "short"}
            }
        },
        "side_effects": {
            "properties": {
                "anxiety": {"type": "short"},
                "dry_mouth": {"type": "short"},
                "paranoia": {"type": "short"},
                "headache": {"type": "short"},
                "dizziness": {"type": "short"},
                "dry_eyes": {"type": "short"},
                "spacey": {"type": "short"},
                "lazy": {"type": "short"},
                "hungry": {"type": "short"},
                "groggy": {"type": "short"},
            }
        },
        "flavor": {
            "properties": {
                "ammonia": {"type": "short"},
                "apple": {"type": "short"},
                "apricot": {"type": "short"},
                "berry": {"type": "short"},
                "blue_cheese": {"type": "short"},
                "blueberry": {"type": "short"},
                "buttery": {"type": "short"},
                "cheese": {"type": "short"},
                "chemical": {"type": "short"},
                "chestnut": {"type": "short"},
                "citrus": {"type": "short"},
                "coffee": {"type": "short"},
                "diesel": {"type": "short"},
                "earthy": {"type": "short"},
                "flowery": {"type": "short"},
                "grape": {"type": "short"},
                "grapefruit": {"type": "short"},
                "herbal": {"type": "short"},
                "honey": {"type": "short"},
                "lavender": {"type": "short"},
                "lemon": {"type": "short"},
                "lime": {"type": "short"},
                "mango": {"type": "short"},
                "menthol": {"type": "short"},
                "minty": {"type": "short"},
                "nutty": {"type": "short"},
                "orange": {"type": "short"},
                "peach": {"type": "short"},
                "pear": {"type": "short"},
                "pepper": {"type": "short"},
                "pine": {"type": "short"},
                "pineapple": {"type": "short"},
                "plum": {"type": "short"},
                "pungent": {"type": "short"},
                "rose": {"type": "short"},
                "sage": {"type": "short"},
                "skunk": {"type": "short"},
                "spicy_herbal": {"type": "short"},
                "strawberry": {"type": "short"},
                "sweet": {"type": "short"},
                "tar": {"type": "short"},
                "tea": {"type": "short"},
                "tobacco": {"type": "short"},
                "tree_fruit": {"type": "short"},
                "tropical": {"type": "short"},
                "vanilla": {"type": "short"},
                "violet": {"type": "short"},
                "woody": {"type": "short"}
            }
        },
        "about": {"type": "string"},
        "origins": {"type": "string"},
        "is_clean": {"type": "boolean"},
        "is_indoor": {"type": "boolean"},
        "name_suggest": {
            "type": "completion",
            "analyzer": "name_analyzer",
            "preserve_separators": True,
            "preserve_position_increments": True,
            "max_input_length": 50
        },
        "locations": {
            "type": "nested",
            "properties": {
                "business_location_id": {"type": "long"},
                "dispensary": {"type": "boolean"},
                "delivery": {"type": "boolean"},
                "grow_house": {"type": "boolean"},
                "delivery_radius": {"type": "float"},
                "location": {"type": "geo_point"},
                "removed_date": {"type": "date"},
                "price_gram": {"type": "float"},
                "price_eighth": {"type": "float"},
                "price_quarter": {"type": "float"},
                "price_half": {"type": "float"},
                "in_stock": {"type": "boolean"}
            }
        }
    }
}

vt_review_mapping = {
    "_parent": {
        "type": TYPES.get('vt')
    },
    "properties": {
        "id": {
            "type": "long"
        },
        "rating": {
            "type": "float"
        },
        "review": {
            "type": "string"
        },
        "review_approved": {
            "type": "boolean"
        },
        "created_date": {
            "type": "date"
        },
        "created_by": {
            "type": "long"
        },
        "last_modified_date": {
            "type": "date"
        },
        "last_modified_by": {
            "type": "long"
        }
    }
}

vt_rating_mapping = {
    "properties": {
        "id": {
            "type": "long"
        },
        "vt_id": {
            "type": "long"
        },
        "user_id": {
            "type": "long"
        },
        "effects": {
            "properties": {
                "happy": {
                    "type": "short"
                },
                "uplifted": {
                    "type": "short"
                },
                "stimulated": {
                    "type": "short"
                },
                "energetic": {
                    "type": "short"
                },
                "creative": {
                    "type": "short"
                },
                "focused": {
                    "type": "short"
                },
                "relaxed": {
                    "type": "short"
                },
                "sleepy": {
                    "type": "short"
                },
                "talkative": {
                    "type": "short"
                },
                "euphoric": {
                    "type": "short"
                },
                "hungry": {
                    "type": "short"
                },
                "tingly": {
                    "type": "short"
                },
                "good_humored": {
                    "type": "short"
                }
            }
        },
        "effects_changed": {
            "type": "boolean"
        },
        "benefits": {
            "properties": {
                "reduce_stress": {
                    "type": "short"
                },
                "help_depression": {
                    "type": "short"
                },
                "relieve_pain": {
                    "type": "short"
                },
                "reduce_fatigue": {
                    "type": "short"
                },
                "reduce_headaches": {
                    "type": "short"
                },
                "help_muscles_spasms": {
                    "type": "short"
                },
                "lower_eye_pressure": {
                    "type": "short"
                },
                "reduce_nausea": {
                    "type": "short"
                },
                "reduce_inflammation": {
                    "type": "short"
                },
                "relieve_cramps": {
                    "type": "short"
                },
                "help_with_seizures": {
                    "type": "short"
                },
                "restore_appetite": {
                    "type": "short"
                },
                "help_with_insomnia": {
                    "type": "short"
                }
            }
        },
        "benefits_changed": {
            "type": "boolean"
        },
        "side_effects": {
            "properties": {
                "anxiety": {
                    "type": "short"
                },
                "dry_mouth": {
                    "type": "short"
                },
                "paranoia": {
                    "type": "short"
                },
                "headache": {
                    "type": "short"
                },
                "dizziness": {
                    "type": "short"
                },
                "dry_eyes": {
                    "type": "short"
                },
                "spacey": {
                    "type": "short"
                },
                "lazy": {
                    "type": "short"
                },
                "hungry": {
                    "type": "short"
                },
                "groggy": {
                    "type": "short"
                }
            }
        },
        "side_effects_changed": {
            "type": "boolean"
        },
        "status": {
            "type": "string"
        },
        "removed_date": {
            "type": "date"
        }
    }
}

business_location_mapping = {
    "properties": {
        "business_id": {"type": "long"},
        "business_location_id": {"type": "long"},
        "category": {"type": "string", "index": "not_analyzed"},
        "slug_name": {"type": "string", "index": "not_analyzed"},
        "location_name": {"type": "string", "index": "not_analyzed"},
        "manager_name": {"type": "string"},
        "location_email": {"type": "string"},
        "dispensary": {"type": "boolean"},
        "delivery": {"type": "boolean"},
        "grow_house": {"type": "boolean"},
        "delivery_radius": {"type": "float"},
        "street1": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string"},
        "zip_code": {"type": "string"},
        "location": {"type": "geo_point"},
        "location_raw": {"type": "string"},
        "phone": {"type": "string"},
        "ext": {"type": "string"},
        "timezone": {"type": "string"},
        "removed_by_id": {"type": "long"},
        "removed_date": {"type": "date"},
        "created_date": {"type": "date"},
        "mon_open": {"type": "string"},
        "mon_close": {"type": "string"},
        "tue_open": {"type": "string"},
        "tue_close": {"type": "string"},
        "wed_open": {"type": "string"},
        "wed_close": {"type": "string"},
        "thu_open": {"type": "string"},
        "thu_close": {"type": "string"},
        "fri_open": {"type": "string"},
        "fri_close": {"type": "string"},
        "sat_open": {"type": "string"},
        "sat_close": {"type": "string"},
        "sun_open": {"type": "string"},
        "sun_close": {"type": "string"},
        "menu_items": {
            "type": "nested",
            "properties": {
                "id": {"type": "long"},
                "vt_id": {"type": "long"},
                "vt_name": {"type": "string"},
                "price_gram": {"type": "float"},
                "price_eighth": {"type": "float"},
                "price_quarter": {"type": "float"},
                "price_half": {"type": "float"},
                "in_stock": {"type": "boolean"},
                "removed_date": {"type": "date"}
            }
        },
        "image": {"type": "string"},
        "url": {"type": "string"},
        "location_name_suggest": {
            "type": "completion",
            "analyzer": "name_analyzer",
            "preserve_separators": True,
            "preserve_position_increments": True,
            "max_input_length": 50,
            "contexts": [
                {
                    "name": "bus_type",
                    "type": "category"
                },
                {
                    "name": "location",
                    "type": "geo",
                    # "precision": '100km',
                    "path": "location"
                }
            ]
        }
    }
}
