"""
Defines various URLs and constants used in the application and for interacting with external APIs
"""

MASON_CONTENT = "application/vnd.mason+json"
JSON_CONTENT = "application/json"
NAMESPACE = "bikinghub"
LINK_RELATIONS_URL = "/link-relations/"
USER_PROFILE = "/profiles/user/"
LOCATION_PROFILE = "/profiles/location/"
WEATHER_PROFILE = "/profiles/weather/"
FAVOURITE_PROFILE = "/profiles/favourite/"
ERROR_PROFILE = "/profiles/error/"

SLIPPERY_URL = "https://liukastumisvaroitus-api.beze.io/api/v1"

FMI_HARMONIE_MULTIPOINT_URL = (
    "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0"
    "&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::multipointcoverage"
)
# &place=oulu

FMI_HARMONIE_SIMPLE_URL = (
    "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0"
    "&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::simple"
)
# &place=oulu

FMI_FORECAST_URL = "https://www.ilmatieteenlaitos.fi/api/weather/forecasts"
# ?place=kaijonharju&area=oulu


MML_URL = "https://avoin-paikkatieto.maanmittauslaitos.fi"

# Cache page size
PAGE_SIZE = 50

# Timeout for cache
CACHE_TIME = 60 * 60 * 24 * 7  # One week
