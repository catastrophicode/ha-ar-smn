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
        "forecast": [
            {
                "date": "2025-01-01",
                "temp_max": 28.0,
                "temp_min": 18.0,
                "weather": {"id": 3, "description": "Despejado"},
                "morning": {
                    "temperature": 20.0,
                    "weather": {"id": 3, "description": "Despejado"},
                    "wind": {"speed": 10.0, "deg": 180},
                },
                "afternoon": {
                    "temperature": 28.0,
                    "weather": {"id": 3, "description": "Despejado"},
                    "wind": {"speed": 15.0, "deg": 180},
                },
                "evening": {
                    "temperature": 24.0,
                    "weather": {"id": 5, "description": "Despejado"},
                    "wind": {"speed": 12.0, "deg": 180},
                },
                "night": {
                    "temperature": 18.0,
                    "weather": {"id": 5, "description": "Despejado"},
                    "wind": {"speed": 8.0, "deg": 180},
                },
            }
        ]
    }


@pytest.fixture
def mock_alerts_data() -> dict:
    """Return mock alerts data."""
    return {
        "warnings": [
            {
                "area_id": "11001",
                "updated": "2025-01-01T10:00:00Z",
                "events": [
                    {
                        "id": 41,  # tormenta
                        "max_level": 3,
                    },
                    {
                        "id": 37,  # lluvia
                        "max_level": 2,
                    },
                ],
            }
        ],
        "reports": [
            {
                "event_id": 41,
                "levels": [
                    {
                        "level": 3,
                        "description": "Tormentas fuertes",
                        "instruction": "Manténgase informado",
                    }
                ],
            },
            {
                "event_id": 37,
                "levels": [
                    {
                        "level": 2,
                        "description": "Lluvias moderadas",
                        "instruction": "Esté atento",
                    }
                ],
            },
        ],
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
