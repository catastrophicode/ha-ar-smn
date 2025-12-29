"""Constants for the SMN integration."""
from typing import Final

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_TIME,
)

DOMAIN: Final = "argentina_smn"
HOME_LOCATION_NAME: Final = "Home"
CONF_TRACK_HOME: Final = "track_home"

# API Endpoints
API_BASE_URL: Final = "https://ws1.smn.gob.ar/v1"
API_COORD_ENDPOINT: Final = f"{API_BASE_URL}/georef/location/coord"
API_FORECAST_ENDPOINT: Final = f"{API_BASE_URL}/forecast/location"
API_ALERT_ENDPOINT: Final = f"{API_BASE_URL}/warning/alert/location"
API_HEAT_WARNING_ENDPOINT: Final = f"{API_BASE_URL}/warning/heat/area"

# Token endpoint
TOKEN_URL: Final = "https://ws2.smn.gob.ar/"

# Default onboarding locations (Buenos Aires)
DEFAULT_HOME_LATITUDE: Final = -34.6037
DEFAULT_HOME_LONGITUDE: Final = -58.3816

# Update intervals
DEFAULT_SCAN_INTERVAL: Final = 3600  # 1 hour in seconds

# Weather condition mappings - SMN to HA
# These will need to be updated based on actual SMN API responses
CONDITIONS_MAP: Final = {
    ATTR_CONDITION_CLEAR_NIGHT: ["despejado noche", "clear night"],
    ATTR_CONDITION_CLOUDY: ["nublado", "cubierto", "cloudy", "overcast"],
    ATTR_CONDITION_FOG: ["niebla", "fog", "neblina"],
    ATTR_CONDITION_PARTLYCLOUDY: [
        "parcialmente nublado",
        "partly cloudy",
        "algo nublado",
        "mayormente nublado",
    ],
    ATTR_CONDITION_RAINY: [
        "lluvia",
        "llovizna",
        "rain",
        "drizzle",
        "chaparron",
        "tormenta",
    ],
    ATTR_CONDITION_SNOWY: ["nieve", "snow", "nevada"],
    ATTR_CONDITION_SUNNY: ["despejado", "soleado", "clear", "sunny"],
}

# Forecast attribute mappings
FORECAST_MAP: Final = {
    ATTR_FORECAST_CONDITION: "condition",
    ATTR_FORECAST_NATIVE_PRECIPITATION: "precipitation",
    ATTR_FORECAST_NATIVE_TEMP: "temperature",
    ATTR_FORECAST_NATIVE_TEMP_LOW: "templow",
    ATTR_FORECAST_NATIVE_WIND_SPEED: "wind_speed",
    ATTR_FORECAST_TIME: "datetime",
}

# Current weather attribute mappings
ATTR_MAP: Final = {
    "temperature": "temp",
    "humidity": "humidity",
    "pressure": "pressure",
    "wind_speed": "wind_speed",
    "wind_bearing": "wind_bearing",
    "visibility": "visibility",
    "description": "description",
}
