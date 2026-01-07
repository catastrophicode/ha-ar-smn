# SMN - Servicio Meteorológico Nacional

Home Assistant integration for Argentina's National Weather Service (Servicio Meteorológico Nacional).

## Features

### Weather Entity
- Current weather conditions (temperature, humidity, pressure, wind)
- Feels-like temperature
- Daily forecast with high/low temperatures
- Hourly forecast details
- Automatic weather condition icons based on SMN data

### Alert Binary Sensors
- **Weather Alert**: Main sensor showing all active alerts
- **Event-specific sensors** for 11 different weather events:
  - Tormenta (Thunderstorm) ⚡
  - Lluvia (Rain) 🌧️
  - Nevada (Snow) ❄️
  - Viento (Wind) 💨
  - Viento Zonda 🌪️
  - Altas Temperaturas (High Temp) 🌡️
  - Bajas Temperaturas (Low Temp) 🥶
  - Niebla (Fog) 🌫️
  - Polvo (Dust) 💨
  - Humo (Smoke) 💨
  - Ceniza Volcánica (Volcanic Ash) 🌋
- **Short-term Alert**: Critical immediate weather warnings
- Home Assistant events fired for automations (`argentina_smn_alert_created`, `argentina_smn_alert_updated`, `argentina_smn_alert_cleared`)

### Services
- `argentina_smn.get_alerts`: Get weather alerts for configured location
- `argentina_smn.get_alerts_for_location`: Get alerts for any location ID

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **SMN**
4. Choose one of:
   - **Track home location**: Automatically uses your Home Assistant location
   - **Custom location**: Enter specific latitude/longitude coordinates

The integration will automatically fetch the location name from SMN's database.

## Data Provided

### Weather Attributes
- Temperature (°C)
- Feels like temperature (°C)
- Humidity (%)
- Atmospheric pressure (hPa)
- Wind speed (km/h) and direction (°)
- Visibility (m)
- Weather condition with appropriate icon

### Alert Attributes
- Active alert count
- Maximum severity level
- Alert summary
- Detailed instructions
- Area ID
- Last updated timestamp

## API Information

This integration uses the SMN public API endpoints:
- Base URL: `https://ws1.smn.gob.ar/v1`
- Authentication: JWT token (automatically managed)
- Update interval: 30 minutes for weather, 10 minutes for alerts

## Credits

Data provided by [Servicio Meteorológico Nacional Argentina](https://www.smn.gob.ar/).
