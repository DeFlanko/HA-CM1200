# Netgear CM1200 MQTT Modem Scraper for Home Assistant

This project lets you monitor your Netgear CM1200 cable modem in Home Assistant by scraping its status page using Playwright, then publishing results to your MQTT broker for easy integration.

---

## Features

- Scrapes all channel stats, SNR, power levels, and system uptime from your modem.
- Publishes each channel/value as a separate MQTT topic.
- Simple Python script—runs externally (PC, Raspberry Pi, server, etc).
- Hassle-free Home Assistant OS/Container compatibility.

---

## Quick Start

### 1. Prerequisites

- You have a working MQTT broker (like Mosquitto) accessible to Home Assistant.
- You can run Python scripts on a system with internet/LAN access to your modem.

### 2. Set Up the Scraper

#### a. Clone or download this repo.

#### b. Install requirements:
```sh
pip install playwright paho-mqtt
playwright install chromium
```

#### c. Edit `cm1200_mqtt_scraper.py`:
- Set your MQTT and modem details at the top of the script.

#### d. Run the script:
```sh
python3 cm1200_mqtt_scraper.py
```

### 3. Add Sensors to Home Assistant

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - name: "CM1200 DS Power Channel 1"
    state_topic: "homeassistant/cm1200/ds_power/channel_1"
    unit_of_measurement: "dBmV"
  - name: "CM1200 US Power Channel 1"
    state_topic: "homeassistant/cm1200/us_power/channel_1"
    unit_of_measurement: "dBmV"
  - name: "CM1200 Downstream Channel Status"
    state_topic: "homeassistant/cm1200/downstream_channel_status"
  - name: "CM1200 System Uptime"
    state_topic: "homeassistant/cm1200/system_uptime"
  # ...repeat for all channels/sensors you want to expose...
```

Or, to get all data in JSON:
```yaml
sensor:
  - platform: mqtt
    name: "CM1200 All Stats"
    state_topic: "homeassistant/cm1200/all"
    value_template: "{{ value_json.system_uptime }}"
    json_attributes_topic: "homeassistant/cm1200/all"
```

---

## Example MQTT Topics

- `homeassistant/cm1200/ds_power/channel_1`
- `homeassistant/cm1200/ds_snr/channel_1`
- `homeassistant/cm1200/system_uptime`
- `homeassistant/cm1200/all` (full JSON blob)

---

## Why External?

Home Assistant OS does not allow installing custom Python packages or browsers. This script runs anywhere you like and integrates perfectly via MQTT!

---

## One-click Add MQTT Integration

[![Open your Home Assistant instance and show the add integration dialog.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mqtt)

---

## Credits

- Inspired by [danieldotnl/ha-multiscrape](https://github.com/danieldotnl/ha-multiscrape)
- Python scraping via [Playwright](https://playwright.dev/python/)
- MQTT with [paho-mqtt](https://pypi.org/project/paho-mqtt/)
