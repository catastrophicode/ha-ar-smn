# SMN Weather Integration

Home Assistant integration for Argentina's National Weather Service (Servicio Meteorológico Nacional).

## Features

- Current weather conditions
- Daily and hourly forecasts
- Weather alerts
- Heat warnings
- Support for multiple locations
- Home location tracking

## Installation

1. Copy the `custom_components/argentina_smn` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration through Settings → Devices & Services → Add Integration
4. Search for "SMN"

## Configuration

During setup, you can either:
- Track your Home Assistant home location automatically
- Configure a specific location with custom latitude/longitude coordinates

## API Endpoints

This integration uses the following SMN API endpoints:

- **Location lookup**: `/v1/georef/location/coord` - Gets location ID from coordinates
- **Forecast**: `/v1/forecast/location/{id}` - Retrieves weather forecast
- **Alerts**: `/v1/warning/alert/location/{id}` - Gets weather alerts
- **Heat warnings**: `/v1/warning/heat/area/{area_id}` - Retrieves heat warnings

## Data Sources

Data is provided by the Servicio Meteorológico Nacional (SMN) - Argentina's official meteorological service.

## License

This integration is provided as-is for use with Home Assistant.
