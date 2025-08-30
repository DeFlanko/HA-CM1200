import asyncio
import json
from paho.mqtt import client as mqtt_client
from playwright.async_api import async_playwright

# ============= USER CONFIGURATION =============
MQTT_BROKER = "<IP or HOSTNAME>"
MQTT_PORT = 1883
MQTT_USER = "homeassistant"
MQTT_PASS = "your_mqtt_password"
MQTT_BASE_TOPIC = "homeassistant/cm1200"

MODEM_URL = "http://192.168.100.1/DocsisStatus.htm"
MODEM_USER = "admin"
MODEM_PASS = "your_modem_password"

INTERVAL = 300  # Scrape interval (seconds)

DOWNSTREAM_CHANNELS = 32
UPSTREAM_CHANNELS = 8
OFDM_CHANNELS = 2
OFDMA_CHANNELS = 2
# ==============================================

DEVICE_INFO = {
    "identifiers": ["cm1200_modem"],
    "name": "CM1200 Cable Modem",
    "model": "Netgear CM1200",
    "manufacturer": "Netgear"
}

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")

def mqtt_publish(client, topic, value, retain=True):
    client.publish(topic, value, retain=retain)

def publish_discovery(mqttc, base_topic):
    # Downstream bonded channels (one entity per channel, all columns as attributes)
    for i in range(DOWNSTREAM_CHANNELS):
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ds_channel_{i+1}/config",
            json.dumps({
                "name": f"CM1200 DS Channel {i+1}",
                "state_topic": f"{base_topic}/ds_channel/{i+1}/state",
                "json_attributes_topic": f"{base_topic}/ds_channel/{i+1}/attributes",
                "unique_id": f"cm1200_ds_channel_{i+1}",
                "device": DEVICE_INFO
            }),
            retain=True
        )

    # Upstream bonded channels (one entity per channel, all columns as attributes)
    for i in range(UPSTREAM_CHANNELS):
        mqttc.publish(
            f"homeassistant/sensor/cm1200_us_channel_{i+1}/config",
            json.dumps({
                "name": f"CM1200 US Channel {i+1}",
                "state_topic": f"{base_topic}/us_channel/{i+1}/state",
                "json_attributes_topic": f"{base_topic}/us_channel/{i+1}/attributes",
                "unique_id": f"cm1200_us_channel_{i+1}",
                "device": DEVICE_INFO
            }),
            retain=True
        )

    # Downstream OFDM channels (one entity per channel, all columns as attributes)
    for i in range(OFDM_CHANNELS):
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ofdm_channel_{i+1}/config",
            json.dumps({
                "name": f"CM1200 OFDM Channel {i+1}",
                "state_topic": f"{base_topic}/ofdm_channel/{i+1}/state",
                "json_attributes_topic": f"{base_topic}/ofdm_channel/{i+1}/attributes",
                "unique_id": f"cm1200_ofdm_channel_{i+1}",
                "device": DEVICE_INFO
            }),
            retain=True
        )

    # Upstream OFDMA channels (one entity per channel, all columns as attributes)
    for i in range(OFDMA_CHANNELS):
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ofdma_channel_{i+1}/config",
            json.dumps({
                "name": f"CM1200 OFDMA Channel {i+1}",
                "state_topic": f"{base_topic}/ofdma_channel/{i+1}/state",
                "json_attributes_topic": f"{base_topic}/ofdma_channel/{i+1}/attributes",
                "unique_id": f"cm1200_ofdma_channel_{i+1}",
                "device": DEVICE_INFO
            }),
            retain=True
        )

    # Modem Status Fields (unchanged)
    status_fields = [
        ("downstream_channel_status", "CM1200 Downstream Channel Status", None),
        ("connectivity_state", "CM1200 Connectivity State", None),
        ("boot_state", "CM1200 Boot State", None),
        ("security_status", "CM1200 Security Status", None),
        ("system_uptime", "CM1200 System Uptime", None),
    ]
    for field, name, unit in status_fields:
        payload = {
            "name": name,
            "state_topic": f"{base_topic}/{field}",
            "unique_id": f"cm1200_{field}",
            "device": DEVICE_INFO
        }
        if unit:
            payload["unit_of_measurement"] = unit
        mqttc.publish(
            f"homeassistant/sensor/cm1200_{field}/config",
            json.dumps(payload),
            retain=True
        )
    # All stats as JSON attributes
    mqttc.publish(
        f"homeassistant/sensor/cm1200_all_stats/config",
        json.dumps({
            "name": "CM1200 All Stats",
            "state_topic": f"{base_topic}/all",
            "value_template": "{{ value_json.system_uptime }}",
            "json_attributes_topic": f"{base_topic}/all",
            "unique_id": "cm1200_all_stats",
            "device": DEVICE_INFO,
        }),
        retain=True
    )

def clean_keys(entry):
    """Convert all keys to lower case and spaces to underscores."""
    return {k.lower().replace(" ", "_"): v for k, v in entry.items()}

async def get_modem_data():
    data = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            http_credentials={"username": MODEM_USER, "password": MODEM_PASS}
        )
        page = await context.new_page()
        try:
            await page.goto(MODEM_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector("#dsTable", timeout=30000)

            # Status fields
            data["downstream_channel_status"] = await page.inner_text("#AcquireDsChanelStatus")
            data["downstream_channel_comment"] = await page.inner_text("#AcquireDsChanelComment")
            data["connectivity_state"] = await page.inner_text("#ConnectivityStateStatus")
            data["connectivity_comment"] = await page.inner_text("#ConnectivityStateComment")
            data["boot_state"] = await page.inner_text("#BootStateStatus")
            data["boot_comment"] = await page.inner_text("#BootStateComment")
            data["security_status"] = await page.inner_text("#SecurityStatus")
            data["security_comment"] = await page.inner_text("#SecurityComment")
            data["system_uptime"] = (await page.inner_text("#SystemUpTime")).replace("System Up Time:","").strip()

            # --- Downstream bonded channels (full row dump) ---
            ds_rows = await page.query_selector_all("#dsTable tr")
            ds_rows = ds_rows[1:]
            downstream_full = []
            for row in ds_rows:
                cells = await row.query_selector_all("td")
                downstream_full.append({
                    "Channel": await cells[0].inner_text(),
                    "Lock Status": await cells[1].inner_text(),
                    "Modulation": await cells[2].inner_text(),
                    "Channel ID": await cells[3].inner_text(),
                    "Frequency": await cells[4].inner_text(),
                    "Power": await cells[5].inner_text(),
                    "SNR": await cells[6].inner_text(),
                    "Correctables": await cells[7].inner_text(),
                    "Uncorrectables": await cells[8].inner_text()
                })
            data["downstream_channels_full"] = downstream_full

            # --- Upstream bonded channels (full row dump) ---
            us_rows = await page.query_selector_all("#usTable tr")
            us_rows = us_rows[1:]
            upstream_full = []
            for row in us_rows:
                cells = await row.query_selector_all("td")
                upstream_full.append({
                    "Channel": await cells[0].inner_text(),
                    "Lock Status": await cells[1].inner_text(),
                    "US Channel Type": await cells[2].inner_text(),
                    "Channel ID": await cells[3].inner_text(),
                    "Symbol Rate": await cells[4].inner_text(),
                    "Frequency": await cells[5].inner_text(),
                    "Power": await cells[6].inner_text()
                })
            data["upstream_channels_full"] = upstream_full

            # --- Downstream OFDM Channels (full row dump) ---
            ofdm_rows = await page.query_selector_all("#dsOfdmTable tr")
            ofdm_rows = ofdm_rows[1:]
            ofdm_full = []
            for row in ofdm_rows:
                cells = await row.query_selector_all("td")
                ofdm_full.append({
                    "Channel": await cells[0].inner_text(),
                    "Lock Status": await cells[1].inner_text(),
                    "Modulation / Profile ID": await cells[2].inner_text(),
                    "Channel ID": await cells[3].inner_text(),
                    "Frequency": await cells[4].inner_text(),
                    "Power": await cells[5].inner_text(),
                    "SNR / MER": await cells[6].inner_text(),
                    "Active Subcarrier Number Range": await cells[7].inner_text(),
                    "Unerrored Codewords": await cells[8].inner_text(),
                    "Correctable Codewords": await cells[9].inner_text(),
                    "Uncorrectable Codewords": await cells[10].inner_text()
                })
            data["ofdm_channels_full"] = ofdm_full

            # --- Upstream OFDMA Channels (full row dump) ---
            ofdma_rows = await page.query_selector_all("#usOfdmaTable tr")
            ofdma_rows = ofdma_rows[1:]
            ofdma_full = []
            for row in ofdma_rows:
                cells = await row.query_selector_all("td")
                ofdma_full.append({
                    "Channel": await cells[0].inner_text(),
                    "Lock Status": await cells[1].inner_text(),
                    "Modulation / Profile ID": await cells[2].inner_text(),
                    "Channel ID": await cells[3].inner_text(),
                    "Frequency": await cells[4].inner_text(),
                    "Power": await cells[5].inner_text()
                })
            data["ofdma_channels_full"] = ofdma_full

        except Exception as e:
            print(f"Scrape error: {e}")
        finally:
            await browser.close()
    return data

async def main():
    mqttc = mqtt_client.Client()
    mqttc.username_pw_set(MQTT_USER, MQTT_PASS)
    mqttc.on_connect = on_connect
    mqttc.connect(MQTT_BROKER, MQTT_PORT)
    mqttc.loop_start()

    publish_discovery(mqttc, MQTT_BASE_TOPIC)

    while True:
        data = await get_modem_data()
        if not data:
            print("No data scraped.")
        else:
            # Downstream bonded channels (per channel, attributes)
            for idx, entry in enumerate(data.get("downstream_channels_full", [])):
                state_topic = f"{MQTT_BASE_TOPIC}/ds_channel/{idx+1}/state"
                attr_topic = f"{MQTT_BASE_TOPIC}/ds_channel/{idx+1}/attributes"
                mqtt_publish(mqttc, state_topic, entry.get("Lock Status", ""))
                mqtt_publish(mqttc, attr_topic, json.dumps(clean_keys(entry)))

            # Upstream bonded channels (per channel, attributes)
            for idx, entry in enumerate(data.get("upstream_channels_full", [])):
                state_topic = f"{MQTT_BASE_TOPIC}/us_channel/{idx+1}/state"
                attr_topic = f"{MQTT_BASE_TOPIC}/us_channel/{idx+1}/attributes"
                mqtt_publish(mqttc, state_topic, entry.get("Lock Status", ""))
                mqtt_publish(mqttc, attr_topic, json.dumps(clean_keys(entry)))

            # Downstream OFDM channels (per channel, attributes)
            for idx, entry in enumerate(data.get("ofdm_channels_full", [])):
                state_topic = f"{MQTT_BASE_TOPIC}/ofdm_channel/{idx+1}/state"
                attr_topic = f"{MQTT_BASE_TOPIC}/ofdm_channel/{idx+1}/attributes"
                mqtt_publish(mqttc, state_topic, entry.get("Lock Status", ""))
                mqtt_publish(mqttc, attr_topic, json.dumps(clean_keys(entry)))

            # Upstream OFDMA channels (per channel, attributes)
            for idx, entry in enumerate(data.get("ofdma_channels_full", [])):
                state_topic = f"{MQTT_BASE_TOPIC}/ofdma_channel/{idx+1}/state"
                attr_topic = f"{MQTT_BASE_TOPIC}/ofdma_channel/{idx+1}/attributes"
                mqtt_publish(mqttc, state_topic, entry.get("Lock Status", ""))
                mqtt_publish(mqttc, attr_topic, json.dumps(clean_keys(entry)))

            # Status fields
            for key in ["downstream_channel_status", "downstream_channel_comment",
                        "connectivity_state", "connectivity_comment",
                        "boot_state", "boot_comment",
                        "security_status", "security_comment",
                        "system_uptime"]:
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/{key}", data.get(key, ""))

            # All stats as JSON
            mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/all", json.dumps(data))
            print("Published modem stats to MQTT.")
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
