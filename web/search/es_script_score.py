MILE = 0.000621371

ADVANCED_SEARCH_SCORE = """
    def total = 0;
    def varietyArray = params["variety"] ?: [];
    def terpenesArray = params['terpenes'] ?: [];
    def cannabinoidsArray = params['cannabinoids'] ?: [];
    def terpenes = params._source.terpenes;
    def cannabinoids = params._source.cannabinoids;
    def cannabinoid_min = 0;
    def cannabinoid_max = 100;
    def delta = 0;
    def cannabinoid = 0;
    
    for (int i = 0; i < terpenesArray.length; ++i){
        if (params.containsKey(terpenesArray[i])){
            if (params[terpenesArray[i]] && terpenes != null && 
                terpenes.containsKey(terpenesArray[i]) && terpenes[terpenesArray[i]] > 0){
                    total += 20;
            }
        }
    }

    if (cannabinoids != null) {
        for (int i = 0; i < cannabinoidsArray.length; ++i){
            cannabinoid_min = 0;
            cannabinoid_max = 100;
            cannabinoid = cannabinoids[cannabinoidsArray[i]];
             
            if (params.containsKey(cannabinoidsArray[i] + '_from')){
                cannabinoid_min = params[cannabinoidsArray[i] + '_from'];
            }
            if (params.containsKey(cannabinoidsArray[i] + '_to')){
                cannabinoid_max = params[cannabinoidsArray[i] + '_to'];
            }
            if (cannabinoid_min >= 0 || cannabinoid_max <= 100){
                total += 100;
            
                if (cannabinoid > cannabinoid_max){
                    delta = cannabinoid - cannabinoid_max;
                } else {
                    delta = cannabinoid_min - cannabinoid;
                }
                         
                if (delta >= (float) (0.75 * cannabinoid)) {
                    total = (float) (total * 0.25);
                } else {
                    if (delta >= (float) (cannabinoid * 0.55)) {total = (float) (total * 0.50)} else {
                        if (delta >= (float) (cannabinoid * 0.20)) {total = (float) (total * 0.75)}
                    }
                }
            }
        }  
    }

    for (int i = 0; i < varietyArray.length; ++i){
        if (params._source.variety == varietyArray[i]) {
            total += 20;
        }
    }

    if (doc['cup_winner'].value && params.containsKey("cup_winner") && params.cup_winner){
        total += 10;
    }
    
    return total;
"""


def advanced_search_nested_location_filter():
    return [{"term": {"locations.in_stock": True}}]


def advanced_search_sort(**kwargs):
    nested_filter = advanced_search_nested_location_filter()
    should_query = [
        {"script": {
            "script": {
                "inline": """
                    def delivery_radius = doc['locations.delivery_radius'].value ?: 0; 
                    return doc['locations.in_stock'].value == true && 
                        doc['locations.delivery'].value == true && delivery_radius >= 
                        doc['locations.location'].planeDistanceWithDefault(
                          params.lat, params.lon, 0) * {}
                    """.format(MILE),
                "lang": "painless",
                "params": {
                    "lat": kwargs.get('lat'),
                    "lon": kwargs.get('lon'),
                    'proximity': kwargs.get('proximity')
                }
            }
        }},
        {"bool": {
            "must": [
                {
                    "geo_distance": {
                        "distance": "{0}mi".format(kwargs.get('proximity')),
                        "distance_type": "plane",
                        "locations.location": {"lat": kwargs.get('lat'), "lon": kwargs.get('lon')}
                    }
                },
                {"match": {'locations.dispensary': True}},
                {"match": {'locations.in_stock': True}},
            ],
            'must_not': [
                {"exists": {"field": "locations.removed_date"}}
            ],
        }}
    ]

    query = {
        "nested_path": "locations",
        'order': 'asc',
        "nested_filter": {
            'bool': {
                'must': nested_filter,
                'must_not': [
                    {"exists": {"field": "locations.removed_date"}}
                ],
                "should": should_query,
                "minimum_should_match": '0<80%'
            }
        }
    }
    query.update(kwargs.get('subquery', {}))
    return query


"""
Groovy script unminified

Workflow:
    - use https://groovyconsole.appspot.com/ to validate script runs
    - minify via http://codebeautify.org/javaviewer (copy only part below comment below that is actual script)

// TEMP for testing syntax

def tp = effectPoints + negEffectPoints + benefitPoints;
return ((float) tp / (float) psa) * 100;​
"""

SRX_RECOMMENDATION_SCORE = ""

CHECK_DELIVERY_RADIUS = """
    def delivery_radius = doc['delivery_radius'].value ?: 0; 
    return 
        doc['delivery'].value == true && delivery_radius >= 
        doc['location'].planeDistanceWithDefault(
          params.lat, params.lon, 0) * {}
    """.format(MILE)
