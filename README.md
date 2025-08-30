# Netgear CM1200 MQTT Discovery Scraper

Monitor your Netgear CM1200 cable modem in Home Assistant—no custom component or YAML required!  
This project uses a Python script to scrape your modem's status page and publish all stats (including channels, SNR, power, frequencies, OFDM/OFDMA, system status, and uptime) to your MQTT broker, with **full Home Assistant MQTT Discovery support**.

---

## Features

**Full MQTT Discovery:** All sensors (including per-channel) are created automatically in Home Assistant
  - All columns from each channel table (Downstream, Upstream, OFDM, OFDMA) are scraped Published as individual MQTT sensors (e.g. `sensor.cm1200_ds_channel_1_lock_status`) and included as attributes in the all-stats sensor (`sensor.cm1200_all_stats`)
- Simple Python script—runs externally (PC, Raspberry Pi, server, etc).
- 100% compatible with Home Assistant OS, Supervised, Container, and Core.

---

## How It Works

1. The Python script (run externally) logs into your modem and scrapes its status page.
2. The script publishes sensor values and Home Assistant MQTT Discovery configs to your MQTT broker.
3. Home Assistant (with MQTT integration enabled) **auto-creates all sensors** for you.
4. You add the sensors to your dashboards and automations—no YAML or files in Home Assistant required!

## Why External?

Home Assistant OS and add-ons do **not** support installing Python packages or browsers securely.  
By running this script on another machine, you get:
- Maximum reliability and security
- No risk to your Home Assistant instance
- No manual YAML maintenance

---

## Prerequisites

- A working MQTT broker (e.g., [Mosquitto](https://mosquitto.org/)) accessible to Home Assistant.
- Python 3 on a machine that can reach your modem and the MQTT broker.
- Home Assistant's [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) enabled and configured.

---

## Setup Instructions

### 1. Clone or Download This Repo

### 2. Install Dependencies
- Python 3.8+
- [Playwright](https://playwright.dev/python/) (`pip install playwright`)
- [paho-mqtt](https://pypi.org/project/paho-mqtt/)
  
On your external system (not on Home Assistant OS):

```sh
pip install playwright paho-mqtt
playwright install chromium
```
## One-click to Add the MQTT Integration in Home Assistant

[![Open your Home Assistant instance and show the add integration dialog.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mqtt)

---

### 3. Edit the Script

Open `cm1200_mqtt_discovery_scraper.py` and set your:

- MQTT broker address/credentials
- Modem IP/credentials (if needed)
- (Optional) Change channel counts if your modem's table is different

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

---
### 4. Run the Script

```sh
python cm1200_mqtt_discovery_scraper.py
```

Leave the script running (or set it as a service/cron job for reliability).

---

## What Happens Next?

- The script scrapes your modem every 5 minutes (default, configurable).
- It publishes all values and MQTT Discovery messages to your MQTT broker.
- **Home Assistant will automatically create all sensors**—no need to edit `configuration.yaml`!
- Find your sensors in Home Assistant under the device "CM1200 Cable Modem".

---

## What Sensors And Attributes Are Exposed?

### Per-Channel Sensors

#### Downstream Bonded Channels
For each of the 32 channels, these sensors are created:
- `sensor.cm1200_ds_channel_X_lock_status`
- `sensor.cm1200_ds_channel_X_modulation`
- `sensor.cm1200_ds_channel_X_channel_id`
- `sensor.cm1200_ds_channel_X_frequency`
- `sensor.cm1200_ds_channel_X_power`
- `sensor.cm1200_ds_channel_X_snr`
- `sensor.cm1200_ds_channel_X_correctables`
- `sensor.cm1200_ds_channel_X_uncorrectables`

#### Upstream Bonded Channels
For each of the 8 channels, these sensors are created:
- `sensor.cm1200_us_channel_X_lock_status`
- `sensor.cm1200_us_channel_X_us_channel_type`
- `sensor.cm1200_us_channel_X_channel_id`
- `sensor.cm1200_us_channel_X_symbol_rate`
- `sensor.cm1200_us_channel_X_frequency`
- `sensor.cm1200_us_channel_X_power`

#### Downstream OFDM Channels
For each of the 2 channels:
- `sensor.cm1200_ofdm_channel_X_lock_status`
- `sensor.cm1200_ofdm_channel_X_modulation_profile_id`
- `sensor.cm1200_ofdm_channel_X_channel_id`
- `sensor.cm1200_ofdm_channel_X_frequency`
- `sensor.cm1200_ofdm_channel_X_power`
- `sensor.cm1200_ofdm_channel_X_snr_mer`
- `sensor.cm1200_ofdm_channel_X_active_subcarrier_range`
- `sensor.cm1200_ofdm_channel_X_unerrored_codewords`
- `sensor.cm1200_ofdm_channel_X_correctable_codewords`
- `sensor.cm1200_ofdm_channel_X_uncorrectable_codewords`

#### Upstream OFDMA Channels
For each of the 2 channels:
- `sensor.cm1200_ofdma_channel_X_lock_status`
- `sensor.cm1200_ofdma_channel_X_modulation_profile_id`
- `sensor.cm1200_ofdma_channel_X_channel_id`
- `sensor.cm1200_ofdma_channel_X_frequency`
- `sensor.cm1200_ofdma_channel_X_power`

### All Stats Sensor

- `sensor.cm1200_all_stats`
  - **Attributes:**  
    - `downstream_channels_full`: List of downstream channel dicts  
      - Each dict has:  
        - Channel, Lock Status, Modulation, Channel ID, Frequency, Power, SNR, Correctables, Uncorrectables
    - `upstream_channels_full`: List of upstream channel dicts  
      - Each dict has:  
        - Channel, Lock Status, US Channel Type, Channel ID, Symbol Rate, Frequency, Power
    - `ofdm_channels_full`: List of OFDM channel dicts  
      - Each dict has:  
        - Channel, Lock Status, Modulation / Profile ID, Channel ID, Frequency, Power, SNR / MER, Active Subcarrier Number Range, Unerrored Codewords, Correctable Codewords, Uncorrectable Codewords
    - `ofdma_channels_full`: List of OFDMA channel dicts  
      - Each dict has:  
        - Channel, Lock Status, Modulation / Profile ID, Channel ID, Frequency, Power
    - Plus all status fields

### Status Sensors

- `sensor.cm1200_downstream_channel_status`
- `sensor.cm1200_connectivity_state`
- `sensor.cm1200_boot_state`
- `sensor.cm1200_security_status`
- `sensor.cm1200_system_uptime`
- ...and their comments

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
> Your modem password and MQTT credentials are stored in plain text.  
> Restrict access to this script and the system running it.

---

## Credits
By [DeFlanko](https://github.com/DeFlanko).  

- Inspired by [danieldotnl/ha-multiscrape](https://github.com/danieldotnl/ha-multiscrape)
- Python scraping via [Playwright](https://playwright.dev/python/)
- MQTT with [paho-mqtt](https://pypi.org/project/paho-mqtt/)

## Project Contributors
<a href="https://github.com/DeFlanko/HA-CM1200/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=DeFlanko/HA-CM1200" />
</a>
