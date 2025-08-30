import asyncio
import json
import time
from paho.mqtt import client as mqtt_client
from playwright.async_api import async_playwright

# ============= USER CONFIGURATION =============
MQTT_BROKER = "YOUR_MQTT_BROKER_IP_OR_HOSTNAME"
MQTT_PORT = 1883
MQTT_USER = "YOUR_MQTT_USERNAME"
MQTT_PASS = "YOUR_MQTT_PASSWORD"
MQTT_BASE_TOPIC = "homeassistant/cm1200"  # All sensors will be under this

MODEM_URL = "http://192.168.100.1/DocsisStatus.htm"
MODEM_USER = None   # Set if needed
MODEM_PASS = None   # Set if needed

INTERVAL = 300  # Scrape interval in seconds

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
    # Downstream Power, SNR, Frequency
    for i in range(1, DOWNSTREAM_CHANNELS + 1):
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ds_power_channel_{i}/config",
            json.dumps({
                "name": f"CM1200 Downstream Power Channel {i}",
                "state_topic": f"{base_topic}/ds_power/channel_{i}",
                "unit_of_measurement": "dBmV",
                "unique_id": f"cm1200_ds_power_channel_{i}",
                "device": DEVICE_INFO
            }),
            retain=True
        )
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ds_snr_channel_{i}/config",
            json.dumps({
                "name": f"CM1200 Downstream SNR Channel {i}",
                "state_topic": f"{base_topic}/ds_snr/channel_{i}",
                "unit_of_measurement": "dB",
                "unique_id": f"cm1200_ds_snr_channel_{i}",
                "device": DEVICE_INFO
            }),
            retain=True
        )
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ds_frequency_channel_{i}/config",
            json.dumps({
                "name": f"CM1200 Downstream Frequency Channel {i}",
                "state_topic": f"{base_topic}/ds_frequencies/channel_{i}",
                "unit_of_measurement": "Hz",
                "unique_id": f"cm1200_ds_frequency_channel_{i}",
                "device": DEVICE_INFO
            }),
            retain=True
        )
    # Upstream Power, Frequency
    for i in range(1, UPSTREAM_CHANNELS + 1):
        mqttc.publish(
            f"homeassistant/sensor/cm1200_us_power_channel_{i}/config",
            json.dumps({
                "name": f"CM1200 Upstream Power Channel {i}",
                "state_topic": f"{base_topic}/us_power/channel_{i}",
                "unit_of_measurement": "dBmV",
                "unique_id": f"cm1200_us_power_channel_{i}",
                "device": DEVICE_INFO
            }),
            retain=True
        )
        mqttc.publish(
            f"homeassistant/sensor/cm1200_us_frequency_channel_{i}/config",
            json.dumps({
                "name": f"CM1200 Upstream Frequency Channel {i}",
                "state_topic": f"{base_topic}/us_frequencies/channel_{i}",
                "unit_of_measurement": "Hz",
                "unique_id": f"cm1200_us_frequency_channel_{i}",
                "device": DEVICE_INFO
            }),
            retain=True
        )
    # OFDM Downstream
    for i in range(1, OFDM_CHANNELS + 1):
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ofdm_power_channel_{i}/config",
            json.dumps({
                "name": f"CM1200 OFDM Downstream Power Channel {i}",
                "state_topic": f"{base_topic}/ofdm_power/channel_{i}",
                "unit_of_measurement": "dBmV",
                "unique_id": f"cm1200_ofdm_power_channel_{i}",
                "device": DEVICE_INFO
            }),
            retain=True
        )
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ofdm_snr_channel_{i}/config",
            json.dumps({
                "name": f"CM1200 OFDM Downstream SNR Channel {i}",
                "state_topic": f"{base_topic}/ofdm_snr/channel_{i}",
                "unit_of_measurement": "dB",
                "unique_id": f"cm1200_ofdm_snr_channel_{i}",
                "device": DEVICE_INFO
            }),
            retain=True
        )
    # OFDMA Upstream
    for i in range(1, OFDMA_CHANNELS + 1):
        mqttc.publish(
            f"homeassistant/sensor/cm1200_ofdma_power_channel_{i}/config",
            json.dumps({
                "name": f"CM1200 OFDMA Upstream Power Channel {i}",
                "state_topic": f"{base_topic}/ofdma_power/channel_{i}",
                "unit_of_measurement": "dBmV",
                "unique_id": f"cm1200_ofdma_power_channel_{i}",
                "device": DEVICE_INFO
            }),
            retain=True
        )
    # Modem Status Fields
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

async def get_modem_data():
    data = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(MODEM_URL, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_selector("table.TableStyle", timeout=10000)
            data["downstream_channel_status"] = await page.inner_text("table.TableStyle tr:nth-child(1) td:nth-child(2)")
            data["connectivity_state"] = await page.inner_text("table.TableStyle tr:nth-child(2) td:nth-child(2)")
            data["boot_state"] = await page.inner_text("table.TableStyle tr:nth-child(3) td:nth-child(2)")
            data["security_status"] = await page.inner_text("table.TableStyle tr:nth-child(5) td:nth-child(2)")
            data["ds_frequencies"] = await page.eval_on_selector_all(
                "#dsTable tr:not(:first-child) td:nth-child(5)",
                "nodes => nodes.map(n => n.innerText.trim())"
            )
            data["ds_power"] = await page.eval_on_selector_all(
                "#dsTable tr:not(:first-child) td:nth-child(6)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dBmV',''))"
            )
            data["ds_snr"] = await page.eval_on_selector_all(
                "#dsTable tr:not(:first-child) td:nth-child(7)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dB',''))"
            )
            data["us_frequencies"] = await page.eval_on_selector_all(
                "#usTable tr:not(:first-child) td:nth-child(6)",
                "nodes => nodes.map(n => n.innerText.trim())"
            )
            data["us_power"] = await page.eval_on_selector_all(
                "#usTable tr:not(:first-child) td:nth-child(7)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dBmV',''))"
            )
            data["ofdm_power"] = await page.eval_on_selector_all(
                "#dsOfdmTable tr:not(:first-child) td:nth-child(6)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dBmV',''))"
            )
            data["ofdm_snr"] = await page.eval_on_selector_all(
                "#dsOfdmTable tr:not(:first-child) td:nth-child(7)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dB',''))"
            )
            data["ofdma_power"] = await page.eval_on_selector_all(
                "#usOfdmaTable tr:not(:first-child) td:nth-child(6)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dBmV',''))"
            )
            data["system_uptime"] = (await page.inner_text("#SystemUpTime")).replace("System Up Time:","").strip()
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

    # Publish MQTT discovery configs at startup
    publish_discovery(mqttc, MQTT_BASE_TOPIC)

    while True:
        data = await get_modem_data()
        if not data:
            print("No data scraped.")
        else:
            # Per-channel values
            for idx in range(DOWNSTREAM_CHANNELS):
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/ds_power/channel_{idx+1}", data.get("ds_power", [None]*DOWNSTREAM_CHANNELS)[idx])
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/ds_snr/channel_{idx+1}", data.get("ds_snr", [None]*DOWNSTREAM_CHANNELS)[idx])
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/ds_frequencies/channel_{idx+1}", data.get("ds_frequencies", [None]*DOWNSTREAM_CHANNELS)[idx])
            for idx in range(UPSTREAM_CHANNELS):
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/us_power/channel_{idx+1}", data.get("us_power", [None]*UPSTREAM_CHANNELS)[idx])
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/us_frequencies/channel_{idx+1}", data.get("us_frequencies", [None]*UPSTREAM_CHANNELS)[idx])
            for idx in range(OFDM_CHANNELS):
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/ofdm_power/channel_{idx+1}", data.get("ofdm_power", [None]*OFDM_CHANNELS)[idx])
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/ofdm_snr/channel_{idx+1}", data.get("ofdm_snr", [None]*OFDM_CHANNELS)[idx])
            for idx in range(OFDMA_CHANNELS):
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/ofdma_power/channel_{idx+1}", data.get("ofdma_power", [None]*OFDMA_CHANNELS)[idx])
            # Status fields
            for key in ["downstream_channel_status", "connectivity_state", "boot_state", "security_status", "system_uptime"]:
                mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/{key}", data.get(key, ""))
            # All stats as JSON
            mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/all", json.dumps(data))
            print("Published modem stats to MQTT.")
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())