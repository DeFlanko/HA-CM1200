# Netgear CM1200 Home Assistant MQTT Scraper

Monitor your Netgear CM1200 cable modem in Home Assistant 
This project scrapes your modem’s web interface and publishes all status, channel, and event log data to your MQTT broker using Home Assistant MQTT Discovery.  
**Home Assistant will automatically create all sensors for you!**

---

## Features

- **Automatic MQTT Discovery:** All modem stats, channels, and event log sensors are auto-created in Home Assistant.
- **Full Modem Status:** Downstream, upstream, OFDM/OFDMA channels, SNR, power, frequencies, system status, uptime, and the full event log.
- **Event Log Table:** Full event log published as a sensor attribute, ideal for dashboard table cards.
- **Simple Python scripts:** Run externally on PC, Raspberry Pi, server, or container.
- **No Home Assistant YAML or custom component required.**
- **Secure:** No additional software installed on your Home Assistant instance.

---

## How It Works

1. The Python script(s) log in to your modem and scrape its status and event log pages.
2. They publish sensor values and MQTT Discovery configs to your MQTT broker.
3. Home Assistant (with MQTT integration enabled) **auto-creates all sensors**—no YAML or manual configuration needed.
4. You add the sensors to your dashboards and automations.

---

## Why Run Externally?

Home Assistant OS and add-ons **cannot** install Python or browsers securely.  
Running this script on another machine provides:
- Maximum reliability and security
- Zero risk to your Home Assistant instance
- No manual YAML maintenance

---

## Prerequisites

- A working MQTT broker (e.g., [Mosquitto](https://mosquitto.org/)), accessible to Home Assistant.
- Python 3.8+ on a machine that can reach your modem and MQTT broker.
- Home Assistant’s [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) enabled and configured.

> [!TIP]
> ### Lovalace Examples
> - I used [flex-table-card](https://github.com/custom-cards/flex-table-card) for the examples in the lovalace folder 

---

## Setup Instructions

### 1. Clone or Download This Repo

```sh
git clone https://github.com/DeFlanko/HA-CM1200.git
cd HA-CM1200
```

### 2. Install Dependencies

```sh
pip install playwright paho-mqtt
playwright install chromium
```

---

### 3. Configure the Scripts

#### **Edit `cm1200_mqtt_discovery_scraper.py` for Status/Channel Data**

Open `cm1200_mqtt_discovery_scraper.py` and set your:

```python
MQTT_BROKER = "your.mqtt.server"
MQTT_PORT = 1883
MQTT_USER = "your_mqtt_username"
MQTT_PASS = "your_mqtt_password"
MQTT_BASE_TOPIC = "homeassistant/cm1200"

MODEM_URL = "http://192.168.100.1/DocsisStatus.htm"
MODEM_USER = "admin"
MODEM_PASS = "your_modem_password"
INTERVAL = 300  # Scrape interval in seconds
```

#### **Edit `cm1200_mqtt_eventlog_scraper.py` for the Event Log**

Open `cm1200_mqtt_eventlog_scraper.py` and set your:

```python
MQTT_BROKER = "your.mqtt.server"
MQTT_PORT = 1883
MQTT_USER = "your_mqtt_username"
MQTT_PASS = "your_mqtt_password"
MQTT_BASE_TOPIC = "homeassistant/cm1200"

MODEM_URL = "http://192.168.100.1/eventLog.htm"
MODEM_USER = "admin"
MODEM_PASS = "your_modem_password"
INTERVAL = 300  # Scrape interval in seconds
```

---

### 4. Run the Scripts

```sh
python cm1200_mqtt_discovery_scraper.py
python cm1200_mqtt_eventlog_scraper.py
```

Leave the scripts running (or use a service/cron for reliability).

---

## What Happens Next?

- The scripts scrape your modem every 5 minutes (default, configurable).
- They publish all values and MQTT Discovery messages to your MQTT broker.
- **Home Assistant will automatically create all sensors**—no need to edit `configuration.yaml`!
- Find your sensors in Home Assistant under the device "CM1200 Cable Modem".

---

## What Sensors and Attributes Are Exposed?

### Status & Channel Sensors (`cm1200_mqtt_discovery_scraper.py`)

- **Per-Channel Sensors:**  
  - Downstream: `sensor.cm1200_ds_channel_X_*` (Lock Status, Modulation, Channel ID, Frequency, Power, SNR, etc)
  - Upstream: `sensor.cm1200_us_channel_X_*` (Lock Status, Channel Type, Channel ID, Symbol Rate, Frequency, Power)
  - OFDM/OFDM-A: `sensor.cm1200_ofdm_channel_X_*`, `sensor.cm1200_ofdma_channel_X_*`
- **Summary/Status Sensors:**  
  - `sensor.cm1200_downstream_channel_status`
  - `sensor.cm1200_connectivity_state`
  - `sensor.cm1200_boot_state`
  - `sensor.cm1200_security_status`
  - `sensor.cm1200_system_uptime`
- **All Stats Sensor:**  
  - `sensor.cm1200_all_stats` — includes all tables as attributes (see script for details).

### Event Log (`cm1200_mqtt_eventlog_scraper.py`)

- **Event Log Sensor:**  
  - `sensor.cm1200_eventlog_entry`
    - **State:** Most recent event (unique hash)
    - **Attributes:**  
      - `log`: List of all event log entries, each containing `time`, `priority`, and `description`
- **New Entries Sensor:**  
  - `sensor.cm1200_eventlog_new` (optional, for automations/notifications of new log entries)


---
> [!WARNING]
> ## Troubleshooting / Debugging
> 
> - **Check `modem_debug.png`** after each run to see what Playwright sees.
> ```python
> await page.goto(MODEM_URL, wait_until="networkidle", timeout=30000)
> # Uncomment to see what the headless browser is rendering:
> # await page.screenshot(path="modem_debug.png")
> # print("Screenshot taken: modem_debug.png")
> await page.wait_for_selector("#dsTable", timeout=30000)
> ``` 
> - If sensors don't appear, check that your script can reach your MQTT broker and that Home Assistant's MQTT integration is enabled.
>   - you can also verify with [MQTT Explorer](https://mqtt-explorer.com/) 
> - Increase the `INTERVAL` (defaulted to 300 seconds "5 mins") if you don't need frequent scraping.
> - Verify your modem's IP and credentials.
> - Check the script's output for errors.

---
> [!CAUTION]
> ## Security Notice
>
> Your modem password and MQTT credentials are stored in plain text.  
> **Restrict access** to this script and the system running it.

---

## Credits

By [DeFlanko](https://github.com/DeFlanko).

- Inspired by [danieldotnl/ha-multiscrape](https://github.com/danieldotnl/ha-multiscrape)
- Python scraping via [Playwright](https://playwright.dev/python/)
- MQTT with [paho-mqtt](https://pypi.org/project/paho-mqtt/)

---

## Contributors

<a href="https://github.com/DeFlanko/HA-CM1200/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=DeFlanko/HA-CM1200" />
</a>
