"""Fixtures for SMN integration tests."""
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_jwt_token() -> str:
    """Return a mock JWT token."""
    # Mock JWT token (header.payload.signature format)
    # Payload includes exp field for expiration testing
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImV4cCI6OTk5OTk5OTk5OX0.signature"


@pytest.fixture
def mock_location_data() -> dict:
    """Return mock location data from georef API."""
    return {
        "id": "4864",
        "name": "Ciudad de Buenos Aires",
        "department": "Comuna 1",
        "province": "Ciudad Autónoma de Buenos Aires",
        "coord": {"lat": -34.6217, "lon": -58.4258},
    }


@pytest.fixture
def mock_current_weather() -> dict:
    """Return mock current weather data."""
    return {
        "temperature": 22.5,
        "feels_like": 21.0,
        "humidity": 65,
        "pressure": 1013.2,
        "visibility": 10000,
        "weather": {"id": 3, "description": "Despejado"},
        "wind": {"speed": 15.5, "deg": 180},
        "location": {
            "id": "4864",
            "name": "Ciudad de Buenos Aires",
            "province": "Ciudad Autónoma de Buenos Aires",
        },
    }


@pytest.fixture
def mock_forecast_data() -> dict:
    """Return mock forecast data."""
    return {
        "updated": "2025-12-30T17:32:59-03:00",
        "location": {
            "id": 4864,
            "name": "Ciudad Autónoma de Buenos Aires",
            "department": "CABA",
            "province": "CABA",
            "type": "Ciudad",
            "coord": {"lon": -58.4258, "lat": -34.6217}
        },
        "type": "location",
        "forecast": [
            {
                "date": "2025-12-30",
                "temp_min": None,
                "temp_max": None,
                "humidity_min": None,
                "humidity_max": None,
                "early_morning": None,
                "morning": None,
                "afternoon": None,
                "night": {
                    "humidity": 30.0,
                    "rain_prob_range": [0, 0],
                    "gust_range": None,
                    "temperature": 31.0,
                    "visibility": "Buena",
                    "rain06h": 0.0,
                    "weather": {"description": "Parcialmente nublado", "id": 25},
                    "wind": {
                        "direction": "NO",
                        "deg": 315.0,
                        "speed_range": [13, 22]
                    },
                    "river": None,
                    "border": None
                }
            },
            {
                "date": "2025-12-31",
                "temp_min": 27.0,
                "temp_max": 39.0,
                "humidity_min": 31.0,
                "humidity_max": 39.0,
                "early_morning": {
                    "humidity": 35.0,
                    "rain_prob_range": [0, 0],
                    "gust_range": [42, 50],
                    "temperature": 27.0,
                    "visibility": "Buena",
                    "rain06h": 0.0,
                    "weather": {"description": "Algo nublado", "id": 19},
                    "wind": {
                        "direction": "NO",
                        "deg": 315.0,
                        "speed_range": [23, 31]
                    },
                    "river": None,
                    "border": None
                },
                "morning": {
                    "humidity": 39.0,
                    "rain_prob_range": [0, 0],
                    "gust_range": None,
                    "temperature": 31.0,
                    "visibility": "Buena",
                    "rain06h": 0.0,
                    "weather": {"description": "Ligeramente nublado", "id": 13},
                    "wind": {
                        "direction": "O",
                        "deg": 292.5,
                        "speed_range": [13, 22]
                    },
                    "river": None,
                    "border": None
                },
                "afternoon": {
                    "humidity": 31.0,
                    "rain_prob_range": [10, 40],
                    "gust_range": None,
                    "temperature": 39.0,
                    "visibility": "Regular",
                    "rain06h": 0.0,
                    "weather": {"description": "Chaparrones", "id": 74},
                    "wind": {
                        "direction": "O",
                        "deg": 292.5,
                        "speed_range": [13, 22]
                    },
                    "river": None,
                    "border": None
                },
                "night": {
                    "humidity": 36.0,
                    "rain_prob_range": [0, 10],
                    "gust_range": None,
                    "temperature": 33.0,
                    "visibility": "Buena",
                    "rain06h": 0.0,
                    "weather": {"description": "Parcialmente nublado", "id": 25},
                    "wind": {
                        "direction": "NO",
                        "deg": 315.0,
                        "speed_range": [13, 22]
                    },
                    "river": None,
                    "border": None
                }
            },
            {
                "date": "2026-01-01",
                "temp_min": 21.0,
                "temp_max": 30.0,
                "humidity_min": 43.0,
                "humidity_max": 66.0,
                "early_morning": {
                    "humidity": 59.0,
                    "rain_prob_range": [0, 0],
                    "gust_range": None,
                    "temperature": 21.0,
                    "visibility": "Buena",
                    "rain06h": 0.0,
                    "weather": {"description": "Parcialmente nublado", "id": 25},
                    "wind": {
                        "direction": "SE",
                        "deg": 135.0,
                        "speed_range": [13, 22]
                    },
                    "river": None,
                    "border": None
                },
                "morning": {
                    "humidity": 56.0,
                    "rain_prob_range": [0, 0],
                    "gust_range": [42, 50],
                    "temperature": 24.0,
                    "visibility": "Buena",
                    "rain06h": 0.0,
                    "weather": {"description": "Mayormente nublado", "id": 37},
                    "wind": {
                        "direction": "SE",
                        "deg": 135.0,
                        "speed_range": [23, 31]
                    },
                    "river": None,
                    "border": None
                },
                "afternoon": {
                    "humidity": 43.0,
                    "rain_prob_range": [0, 0],
                    "gust_range": None,
                    "temperature": 30.0,
                    "visibility": "Buena",
                    "rain06h": 0.1,
                    "weather": {"description": "Parcialmente nublado", "id": 25},
                    "wind": {
                        "direction": "NE",
                        "deg": 67.5,
                        "speed_range": [13, 22]
                    },
                    "river": None,
                    "border": None
                },
                "night": {
                    "humidity": 66.0,
                    "rain_prob_range": [0, 0],
                    "gust_range": None,
                    "temperature": 24.0,
                    "visibility": "Buena",
                    "rain06h": 0.0,
                    "weather": {"description": "Parcialmente nublado", "id": 25},
                    "wind": {
                        "direction": "E",
                        "deg": 90.0,
                        "speed_range": [13, 22]
                    },
                    "river": None,
                    "border": None
                }
            }
        ]
    }


@pytest.fixture
def mock_alerts_data() -> dict:
    """Return mock alerts data with no active alerts (all level 1)."""
    return {
        "area_id": 762,
        "updated": "2025-12-30T17:33:07-03:00",
        "warnings": [
            {
                "date": "2025-12-30",
                "max_level": 1,
                "events": [
                    {
                        "id": 37,
                        "max_level": 1,
                        "levels": {
                            "early_morning": None,
                            "morning": None,
                            "afternoon": None,
                            "night": 1
                        }
                    },
                    {
                        "id": 54,
                        "max_level": 1,
                        "levels": {
                            "early_morning": None,
                            "morning": None,
                            "afternoon": None,
                            "night": 1
                        }
                    },
                    {
                        "id": 39,
                        "max_level": 1,
                        "levels": {
                            "early_morning": None,
                            "morning": None,
                            "afternoon": None,
                            "night": 1
                        }
                    },
                    {
                        "id": 40,
                        "max_level": 1,
                        "levels": {
                            "early_morning": None,
                            "morning": None,
                            "afternoon": None,
                            "night": 1
                        }
                    },
                    {
                        "id": 41,
                        "max_level": 1,
                        "levels": {
                            "early_morning": None,
                            "morning": None,
                            "afternoon": None,
                            "night": 1
                        }
                    },
                    {
                        "id": 42,
                        "max_level": 1,
                        "levels": {
                            "early_morning": None,
                            "morning": None,
                            "afternoon": None,
                            "night": 1
                        }
                    }
                ]
            }
        ],
        "reports": []
    }


@pytest.fixture
def mock_alerts_data_with_active() -> dict:
    """Return mock alerts data with active alerts (for testing alert sensors)."""
    return {
        "area_id": 762,
        "updated": "2025-12-30T17:33:07-03:00",
        "warnings": [
            {
                "date": "2025-12-30",
                "max_level": 3,
                "events": [
                    {
                        "id": 41,  # tormenta
                        "max_level": 3,
                        "levels": {
                            "early_morning": None,
                            "morning": None,
                            "afternoon": None,
                            "night": 3
                        }
                    },
                    {
                        "id": 37,  # lluvia
                        "max_level": 2,
                        "levels": {
                            "early_morning": None,
                            "morning": None,
                            "afternoon": None,
                            "night": 2
                        }
                    }
                ]
            }
        ],
        "reports": [
            {
                "event_id": 41,
                "levels": [
                    {
                        "level": 3,
                        "description": "Tormentas fuertes",
                        "instruction": "Manténgase informado"
                    }
                ]
            },
            {
                "event_id": 37,
                "levels": [
                    {
                        "level": 2,
                        "description": "Lluvias moderadas",
                        "instruction": "Esté atento"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_shortterm_alerts() -> list:
    """Return mock short-term alerts data."""
    return [
        {
            "id": 30060,
            "title": "TORMENTAS FUERTES CON RAFAGAS Y OCASIONAL CAIDA DE GRANIZO. ",
            "date": "2025-12-30T19:42:00-03:00",
            "end_date": "2025-12-30T20:42:00-03:00",
            "zones": [
                "BUENOS AIRES: Ayacucho - Balcarce - Mar Chiquita."
            ],
            "severity": "N",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-58.76, -37.23],
                        [-58.2, -37.61],
                        [-57.8, -37.3],
                        [-58.24, -36.95]
                    ]
                ]
            },
            "images": [
                {
                    "title": "gmp_general",
                    "url": "http://estaticos.smn.gob.ar/pronosticos/avisomet/datos_aviso/HkuFGi0TlWNom4e/avi_gral.gif"
                }
            ],
            "region": "Sector Centro",
            "partial": "Y",
            "provinces": [
                {
                    "id": 6,
                    "name": "Buenos Aires",
                    "locations": [4268, 4289, 4290, 4293]
                }
            ],
            "instructions": "1- Retirá o asegurá objetos que puedan ser arrastrados por el viento.\n2- Cerrá y alejate de puertas y ventanas.\n3- No te refugies debajo de marquesinas, carteles publicitarios, árboles o postes.\n4- Permanecé en construcciones cerradas como casas, escuelas o edificios públicos.\n5- Mantenete alejado de artefactos eléctricos y evitá el uso de teléfonos con cable.\n6- Si estás al aire libre, buscá refugio inmediato en un edificio, casa o vehículo cerrado.\n7- Para minimizar el riesgo de ser alcanzado por un rayo, no permanezcas en playas, ríos, lagunas o piletas."
        }
    ]


@pytest.fixture
def mock_token_manager() -> Generator[MagicMock, None, None]:
    """Mock the SMN token manager."""
    with patch(
        "custom_components.argentina_smn.coordinator.SMNTokenManager"
    ) as mock_manager:
        manager_instance = mock_manager.return_value
        manager_instance.get_token = AsyncMock(
            return_value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk5OTk5OTk5OTl9.sig"
        )
        manager_instance.fetch_token = AsyncMock(
            return_value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk5OTk5OTk5OTl9.sig"
        )
        yield manager_instance


@pytest.fixture
def mock_aiohttp_session() -> Generator[MagicMock, None, None]:
    """Mock aiohttp session for API calls."""
    with patch("aiohttp.ClientSession") as mock_session:
        session_instance = MagicMock()
        mock_session.return_value = session_instance

        # Mock response
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock()

        # Setup context manager
        mock_get = AsyncMock()
        mock_get.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.__aexit__ = AsyncMock()

        session_instance.get = MagicMock(return_value=mock_get)

        yield session_instance


@pytest.fixture
def mock_coordinator_data(
    mock_current_weather, mock_forecast_data, mock_alerts_data, mock_shortterm_alerts
) -> dict:
    """Return mock coordinator data."""
    return {
        "current_weather_data": mock_current_weather,
        "daily_forecast": mock_forecast_data.get("forecast", []),
        "hourly_forecast": [],
        "alerts": mock_alerts_data,
        "shortterm_alerts": mock_shortterm_alerts,
        "heat_warnings": {},
    }
