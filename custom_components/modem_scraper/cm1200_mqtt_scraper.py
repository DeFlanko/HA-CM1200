import asyncio
import json
import time
from paho.mqtt import client as mqtt_client
from playwright.async_api import async_playwright

# MQTT Configuration
MQTT_BROKER = "mqtt.your.local.ip"
MQTT_PORT = 1883
MQTT_USER = "your_mqtt_username"
MQTT_PASS = "your_mqtt_password"
MQTT_BASE_TOPIC = "homeassistant/cm1200"  # All sensors will be under this

# Modem Status Page
MODEM_URL = "http://192.168.100.1/DocsisStatus.htm"
MODEM_USER = None   # Set if needed
MODEM_PASS = None   # Set if needed

# Scrape interval (seconds)
INTERVAL = 300

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")

def mqtt_publish(client, topic, value, retain=True):
    client.publish(topic, value, retain=retain)

async def get_modem_data():
    data = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(MODEM_URL, wait_until="domcontentloaded", timeout=20000)
            # Wait for main table
            await page.wait_for_selector("table.TableStyle", timeout=10000)
            # Startup Procedure
            data["downstream_channel_status"] = await page.inner_text("table.TableStyle tr:nth-child(1) td:nth-child(2)")
            data["connectivity_state"] = await page.inner_text("table.TableStyle tr:nth-child(2) td:nth-child(2)")
            data["boot_state"] = await page.inner_text("table.TableStyle tr:nth-child(3) td:nth-child(2)")
            data["security_status"] = await page.inner_text("table.TableStyle tr:nth-child(5) td:nth-child(2)")
            # Downstream Bonded Channels
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
            # Upstream Bonded Channels
            data["us_frequencies"] = await page.eval_on_selector_all(
                "#usTable tr:not(:first-child) td:nth-child(6)",
                "nodes => nodes.map(n => n.innerText.trim())"
            )
            data["us_power"] = await page.eval_on_selector_all(
                "#usTable tr:not(:first-child) td:nth-child(7)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dBmV',''))"
            )
            # OFDM Channels
            data["ofdm_power"] = await page.eval_on_selector_all(
                "#dsOfdmTable tr:not(:first-child) td:nth-child(6)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dBmV',''))"
            )
            data["ofdm_snr"] = await page.eval_on_selector_all(
                "#dsOfdmTable tr:not(:first-child) td:nth-child(7)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dB',''))"
            )
            # OFDMA Channels
            data["ofdma_power"] = await page.eval_on_selector_all(
                "#usOfdmaTable tr:not(:first-child) td:nth-child(6)",
                "nodes => nodes.map(n => n.innerText.trim().replace(' dBmV',''))"
            )
            # System Uptime
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

    while True:
        data = await get_modem_data()
        if not data:
            print("No data scraped.")
        else:
            # Publish each sensor/channel
            for key, value in data.items():
                if isinstance(value, list):
                    for idx, v in enumerate(value):
                        channel_topic = f"{MQTT_BASE_TOPIC}/{key}/channel_{idx+1}"
                        mqtt_publish(mqttc, channel_topic, v)
                else:
                    mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/{key}", value)
            # Publish all as JSON too
            mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/all", json.dumps(data))
            print("Published modem stats to MQTT.")
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())