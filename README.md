# Netgear CM1200 MQTT Modem Scraper for Home Assistant

Monitor your Netgear CM1200 cable modem in Home Assistant—no custom component or YAML required!  
This project uses a Python script to scrape your modem's status page and publish all stats (including channels, SNR, power, frequencies, OFDM/OFDMA, system status, and uptime) to your MQTT broker, with **full Home Assistant MQTT Discovery support**.

---

## Features

- **Full MQTT Discovery:** All sensors (including per-channel) are created automatically in Home Assistant—no YAML needed!
- Scrapes downstream, upstream, OFDM, OFDMA, and summary/status fields from your modem.
- Simple Python script—runs externally (PC, Raspberry Pi, server, etc).
- 100% compatible with Home Assistant OS, Supervised, Container, and Core.

---

## How It Works

1. The Python script (run externally) logs into your modem and scrapes its status page.
2. The script publishes sensor values and Home Assistant MQTT Discovery configs to your MQTT broker.
3. Home Assistant (with MQTT integration enabled) **auto-creates all sensors** for you.
4. You add the sensors to your dashboards and automations—no YAML or files in Home Assistant required!

---

## Prerequisites

- A working MQTT broker (e.g., [Mosquitto](https://mosquitto.org/)) accessible to Home Assistant.
- Python 3 on a machine that can reach your modem and the MQTT broker.
- Home Assistant's [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) enabled and configured.

---

## Setup Instructions

### 1. Clone or Download This Repo

### 2. Install Dependencies

On your external system (not on Home Assistant OS):

```sh
pip install playwright paho-mqtt
playwright install chromium
```

### 3. Edit the Script

Open `cm1200_mqtt_discovery_scraper.py` and set your:

- MQTT broker address/credentials
- Modem IP/credentials (if needed)
- (Optional) Change channel counts if your modem's table is different

### 4. Run the Script

```sh
python3 cm1200_mqtt_discovery_scraper.py
```

Leave the script running (or set it as a service/cron job for reliability).

---

## What Happens Next?

- The script scrapes your modem every 5 minutes (default, configurable).
- It publishes all values and MQTT Discovery messages to your MQTT broker.
- **Home Assistant will automatically create all sensors**—no need to edit `configuration.yaml`!
- Find your sensors in Home Assistant under the device "CM1200 Cable Modem".

---

## Example Sensors Created

- CM1200 Downstream Power Channel 1–32
- CM1200 Downstream SNR Channel 1–32
- CM1200 Downstream Frequency Channel 1–32
- CM1200 Upstream Power Channel 1–8
- CM1200 Upstream Frequency Channel 1–8
- CM1200 OFDM Downstream Power/SNR Channel 1–2
- CM1200 OFDMA Upstream Power Channel 1–2
- CM1200 Downstream Channel Status
- CM1200 Connectivity State
- CM1200 Boot State
- CM1200 Security Status
- CM1200 System Uptime
- CM1200 All Stats (JSON attributes, for advanced dashboards)

If your modem has fewer/more channels, adjust the script configuration.

---

## Home Assistant Configuration

**No YAML or custom files needed!**  
Just make sure the MQTT integration is enabled and connected to your broker.

---

## Why External?

Home Assistant OS and add-ons do **not** support installing Python packages or browsers securely.  
By running this script on another machine, you get:
- Maximum reliability and security
- No risk to your Home Assistant instance
- No manual YAML maintenance

---

## One-click Add MQTT Integration

[![Open your Home Assistant instance and show the add integration dialog.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mqtt)

---

## Troubleshooting

- If sensors don't appear, check that your script can reach your MQTT broker and that Home Assistant's MQTT integration is enabled.
- Verify your modem's IP and credentials.
- Check the script's output for errors.

---

## Credits

- Inspired by [danieldotnl/ha-multiscrape](https://github.com/danieldotnl/ha-multiscrape)
- Python scraping via [Playwright](https://playwright.dev/python/)
- MQTT with [paho-mqtt](https://pypi.org/project/paho-mqtt/)

---
