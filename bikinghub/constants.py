"""
Defines various URLs and constants used in the application and for interacting with external APIs
"""

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

MML_API_KEY = ""  # Replace with your API key

# Cache page size
PAGE_SIZE = 50

# Timeout for cache
CACHE_TIME = 60 * 60 * 24 * 7  # One week
