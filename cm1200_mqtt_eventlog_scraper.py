import asyncio
import json
import os
import hashlib
from paho.mqtt import client as mqtt_client
from playwright.async_api import async_playwright

# ============= USER CONFIGURATION =============
MQTT_BROKER = "<MQTT IP OR HOSTANME>"
MQTT_PORT = 1883
MQTT_USER = "<MQTT USERNAME>"
MQTT_PASS = "<MQTT PASSWORD>"
MQTT_BASE_TOPIC = "homeassistant/cm1200"

MODEM_URL = "http://192.168.100.1/eventLog.htm"
MODEM_USER = "<CABLE MODEM USERNAME>"
MODEM_PASS = "<CABLE MODEM PASSWORD>"

INTERVAL = 300  # Scrape interval (seconds)
SENT_EVENTLOG_FILE = "sent_eventlog.json"
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
    # Discovery for the event log entity
    mqttc.publish(
        f"homeassistant/sensor/cm1200_eventlog_entry/config",
        json.dumps({
            "name": "CM1200 Event Log",
            "unique_id": "cm1200_eventlog_entry",
            "state_topic": f"{base_topic}/eventlog_entry/state",
            "json_attributes_topic": f"{base_topic}/eventlog_entry/attributes",
            "device": DEVICE_INFO,
        }),
        retain=True
    )

def event_hash(time, priority, description):
    s = f"{time}|{priority}|{description}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_sent_events():
    if os.path.exists(SENT_EVENTLOG_FILE):
        try:
            with open(SENT_EVENTLOG_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_sent_events(sent_hashes):
    try:
        with open(SENT_EVENTLOG_FILE, "w") as f:
            json.dump(list(sent_hashes), f)
    except Exception as e:
        print(f"Could not save sent event log hashes: {e}")

async def get_modem_eventlog():
    entries = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            http_credentials={"username": MODEM_USER, "password": MODEM_PASS}
        )
        page = await context.new_page()
        try:
            await page.goto(MODEM_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector("#EventLogTable", timeout=30000)
            log_rows = await page.query_selector_all("#EventLogTable tr")
            for row in log_rows[1:]:  # skip header
                cells = await row.query_selector_all("td")
                if len(cells) < 3:
                    continue
                time_val = (await cells[0].inner_text()).strip()
                priority = (await cells[1].inner_text()).strip()
                description = (await cells[2].inner_text()).strip()
                entries.append({
                    "time": time_val,
                    "priority": priority,
                    "description": description
                })
        except Exception as e:
            print(f"Scrape error: {e}")
        finally:
            await browser.close()
    return entries

async def main():
    mqttc = mqtt_client.Client()
    mqttc.username_pw_set(MQTT_USER, MQTT_PASS)
    mqttc.on_connect = on_connect
    mqttc.connect(MQTT_BROKER, MQTT_PORT)
    mqttc.loop_start()

    publish_discovery(mqttc, MQTT_BASE_TOPIC)

    sent_hashes = load_sent_events()

    while True:
        entries = await get_modem_eventlog()
        # Newest to oldest so newest is always the state
        new_events = []
        for entry in entries:
            h = event_hash(entry["time"], entry["priority"], entry["description"])
            if h not in sent_hashes:
                new_events.append((h, entry))
        # Always publish the full log as an attribute
        full_log_payload = {
            "log": entries
        }
        mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/eventlog_entry/attributes", json.dumps(full_log_payload))
        # Send each new event (oldest first for logical ordering)
        for h, entry in reversed(new_events):
            # Publish state (hash) and latest attributes (the entry is the latest, but log is always in attributes)
            mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/eventlog_entry/state", h)
            print(f"Published event: {entry}")
            sent_hashes.add(h)
            save_sent_events(sent_hashes)  # Save after each to persist on crash
        if not new_events:
            print("No new event log entries.")
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
