# SMN - Servicio Meteorológico Nacional

Home Assistant integration for Argentina's National Weather Service (Servicio Meteorológico Nacional).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

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

## Installation

### HACS (Recommended)
1. Add this repository as a custom repository in HACS
2. Search for "SMN" in HACS
3. Click Install
4. Restart Home Assistant

### Manual
1. Copy the `custom_components/argentina_smn` folder to your `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **SMN**
4. Choose one of:
   - **Track home location**: Automatically uses your Home Assistant location
   - **Custom location**: Enter specific latitude/longitude coordinates

The integration will automatically fetch the location name from SMN's database.

## Example Automations

### Alert Notification
```yaml
automation:
  - alias: "SMN Weather Alert Notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.ciudad_de_buenos_aires_weather_alert
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Alerta Meteorológica"
          message: "{{ state_attr('binary_sensor.ciudad_de_buenos_aires_weather_alert', 'alert_summary') }}"
```

### Storm Alert
```yaml
automation:
  - alias: "Storm Alert - Close Windows"
    trigger:
      - platform: state
        entity_id: binary_sensor.ciudad_de_buenos_aires_alert_tormenta
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Alerta de Tormenta"
          message: "Cierra las ventanas - {{ state_attr('binary_sensor.ciudad_de_buenos_aires_alert_tormenta', 'description') }}"
```

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

## Troubleshooting

### Integration fails to load
- Verify your internet connection
- Check Home Assistant logs for errors: `Settings → System → Logs`
- Restart Home Assistant

### Weather data not updating
- The integration updates every 30 minutes
- Check the coordinator last update time in Developer Tools → States
- Verify SMN API is accessible from your network

### Location not found
- Ensure coordinates are within Argentina
- Try slightly different coordinates if your exact location isn't in SMN's database
- Use coordinates of nearby major cities

### Enable debug logging
Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.argentina_smn: debug
```

## Credits

Data provided by [Servicio Meteorológico Nacional Argentina](https://www.smn.gob.ar/).

## License

This integration is provided as-is under the MIT License.
