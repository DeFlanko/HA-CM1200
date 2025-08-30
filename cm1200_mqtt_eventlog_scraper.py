import asyncio
import json
import os
from paho.mqtt import client as mqtt_client
from playwright.async_api import async_playwright

# ============= USER CONFIGURATION =============
MQTT_BROKER = "172.10.1.31"
MQTT_PORT = 1883
MQTT_USER = "homeassistant"
MQTT_PASS = "aic7Bai2aephe1oathai7siPhoo4uf0gah3ao5iurai4Eighuu9noonei2Pu8Ahj"
MQTT_BASE_TOPIC = "homeassistant/cm1200"

MODEM_URL = "http://192.168.100.1/eventLog.htm"
MODEM_USER = "admin"
MODEM_PASS = "P00lp@rty!"

INTERVAL = 300  # Scrape interval (seconds)
LAST_EVENTLOG_FILE = "last_eventlog_time.json"
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
    # Discovery for event log sensor (full log as attributes, most recent entry as state)
    mqttc.publish(
        f"homeassistant/sensor/cm1200_eventlog/config",
        json.dumps({
            "name": "CM1200 Event Log",
            "state_topic": f"{base_topic}/eventlog",
            "value_template": "{{ value_json.latest_entry }}",
            "json_attributes_topic": f"{base_topic}/eventlog",
            "unique_id": "cm1200_eventlog",
            "device": DEVICE_INFO,
        }),
        retain=True
    )
    # Discovery for "new entries" sensor (state is count, attribute is new entries)
    mqttc.publish(
        f"homeassistant/sensor/cm1200_eventlog_new/config",
        json.dumps({
            "name": "CM1200 Event Log New Entries",
            "state_topic": f"{base_topic}/eventlog_new",
            "value_template": "{{ value_json.new_count }}",
            "json_attributes_topic": f"{base_topic}/eventlog_new",
            "unique_id": "cm1200_eventlog_new",
            "device": DEVICE_INFO,
        }),
        retain=True
    )

async def get_modem_eventlog():
    data = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            http_credentials={"username": MODEM_USER, "password": MODEM_PASS}
        )
        page = await context.new_page()
        try:
            await page.goto(MODEM_URL, wait_until="networkidle", timeout=30000)
            await page.screenshot(path="modem_eventlog_debug.png")
            print("Screenshot taken: modem_eventlog_debug.png")
            await page.wait_for_selector("#EventLogTable", timeout=30000)

            log_rows = await page.query_selector_all("#EventLogTable tr")
            log_entries = []
            for row in log_rows[1:]:  # skip header
                cells = await row.query_selector_all("td")
                if len(cells) < 3:
                    continue
                time_val = (await cells[0].inner_text()).strip()
                priority = (await cells[1].inner_text()).strip()
                description = (await cells[2].inner_text()).strip()
                log_entries.append({
                    "time": time_val,
                    "priority": priority,
                    "description": description
                })
            data["entries"] = log_entries
            if log_entries:
                latest = log_entries[0]
                data["latest_entry"] = f"{latest['time']} {latest['priority']} {latest['description']}"
            else:
                data["latest_entry"] = ""
        except Exception as e:
            print(f"Scrape error: {e}")
        finally:
            await browser.close()
    return data

def load_last_sent_time():
    # Returns the last sent log entry time, or None if not found
    if os.path.exists(LAST_EVENTLOG_FILE):
        try:
            with open(LAST_EVENTLOG_FILE, "r") as f:
                return json.load(f).get("last_time")
        except Exception:
            return None
    return None

def save_last_sent_time(last_time):
    try:
        with open(LAST_EVENTLOG_FILE, "w") as f:
            json.dump({"last_time": last_time}, f)
    except Exception as e:
        print(f"Could not save last event log time: {e}")

async def main():
    mqttc = mqtt_client.Client()
    mqttc.username_pw_set(MQTT_USER, MQTT_PASS)
    mqttc.on_connect = on_connect
    mqttc.connect(MQTT_BROKER, MQTT_PORT)
    mqttc.loop_start()

    publish_discovery(mqttc, MQTT_BASE_TOPIC)

    last_time = load_last_sent_time()

    while True:
        data = await get_modem_eventlog()
        entries = data.get("entries", [])
        # Publish full log (for HA attribute use)
        mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/eventlog", json.dumps(data))
        print("Published complete modem event log to MQTT.")

        # Only publish new entries since last_time
        new_entries = []
        for entry in entries:
            if last_time and entry["time"] == last_time:
                break  # Stop at last sent entry
            new_entries.append(entry)
        if new_entries:
            # Send new entries (oldest first for easier reading)
            to_send = list(reversed(new_entries))
            mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/eventlog_new", json.dumps({
                "new_entries": to_send,
                "new_count": len(to_send)
            }))
            print(f"Published {len(to_send)} new modem event log entries to MQTT.")
            # Update last_time
            last_time = entries[0]["time"]  # Top of the table is always most recent
            save_last_sent_time(last_time)
        else:
            # Still publish empty so HA can clear state
            mqtt_publish(mqttc, f"{MQTT_BASE_TOPIC}/eventlog_new", json.dumps({
                "new_entries": [],
                "new_count": 0
            }))
            print("No new log entries.")
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())