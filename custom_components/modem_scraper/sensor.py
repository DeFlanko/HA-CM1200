import logging
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_URL, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv
from .playwright_scraper import async_get_modem_data

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = 300

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_URL): cv.url,
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
})

# Keys that return lists and should be expanded into multiple sensors
LIST_KEYS = [
    "ds_frequencies",
    "ds_power",
    "ds_snr",
    "us_frequencies",
    "us_power",
    "ofdm_power",
    "ofdm_snr",
    "ofdma_power",
]

# Keys that return single values
SINGLE_KEYS = [
    "downstream_channel_status",
    "connectivity_state",
    "boot_state",
    "security_status",
    "system_uptime",
]

# Units and attributes for each key
SENSOR_ATTRIBUTES = {
    "ds_frequencies": {"device_class": None, "unit_of_measurement": "Hz", "icon": "mdi:waves"},
    "ds_power": {"device_class": None, "unit_of_measurement": "dBmV", "icon": "mdi:flash"},
    "ds_snr": {"device_class": None, "unit_of_measurement": "dB", "icon": "mdi:signal"},
    "us_frequencies": {"device_class": None, "unit_of_measurement": "Hz", "icon": "mdi:waves"},
    "us_power": {"device_class": None, "unit_of_measurement": "dBmV", "icon": "mdi:flash"},
    "ofdm_power": {"device_class": None, "unit_of_measurement": "dBmV", "icon": "mdi:flash"},
    "ofdm_snr": {"device_class": None, "unit_of_measurement": "dB", "icon": "mdi:signal"},
    "ofdma_power": {"device_class": None, "unit_of_measurement": "dBmV", "icon": "mdi:flash"},
    "downstream_channel_status": {"device_class": None, "unit_of_measurement": None, "icon": "mdi:lan-connect"},
    "connectivity_state": {"device_class": None, "unit_of_measurement": None, "icon": "mdi:lan"},
    "boot_state": {"device_class": None, "unit_of_measurement": None, "icon": "mdi:power-cycle"},
    "security_status": {"device_class": None, "unit_of_measurement": None, "icon": "mdi:shield-check"},
    "system_uptime": {"device_class": None, "unit_of_measurement": None, "icon": "mdi:clock-outline"},
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    url = config[CONF_URL]
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    scan_interval = config[CONF_SCAN_INTERVAL]

    # Get initial data to determine channel counts
    data = await async_get_modem_data(url, username, password)
    sensors = []

    # Sensors for single-value keys
    for key in SINGLE_KEYS:
        sensors.append(ModemScrapeSensor(key, url, username, password))

    # Sensors for list-value keys, create one per value
    for key in LIST_KEYS:
        values = data.get(key, [])
        for idx in range(len(values)):
            sensors.append(ModemScrapeListSensor(key, url, username, password, idx))

    async_add_entities(sensors, update_before_add=True)

class ModemScrapeSensor(SensorEntity):
    def __init__(self, key, url, username, password):
        self._attr_name = f"Modem {key.replace('_', ' ').title()}"
        self.url = url
        self.username = username
        self.password = password
        self.key = key
        self._attr_state = None
        self._attr_device_class = SENSOR_ATTRIBUTES.get(key, {}).get("device_class")
        self._attr_unit_of_measurement = SENSOR_ATTRIBUTES.get(key, {}).get("unit_of_measurement")
        self._attr_icon = SENSOR_ATTRIBUTES.get(key, {}).get("icon")
        self._attr_extra_state_attributes = {}

    async def async_update(self):
        data = await async_get_modem_data(self.url, self.username, self.password)
        value = data.get(self.key)
        self._attr_state = value if value is not None else "unavailable"
        # Add all modem data as attributes, excluding large lists
        self._attr_extra_state_attributes = {k: v for k, v in data.items() if k not in LIST_KEYS}

class ModemScrapeListSensor(SensorEntity):
    def __init__(self, key, url, username, password, idx):
        self._attr_name = f"Modem {key.replace('_', ' ').title()} Channel {idx+1}"
        self.url = url
        self.username = username
        self.password = password
        self.key = key
        self.idx = idx
        self._attr_state = None
        self._attr_device_class = SENSOR_ATTRIBUTES.get(key, {}).get("device_class")
        self._attr_unit_of_measurement = SENSOR_ATTRIBUTES.get(key, {}).get("unit_of_measurement")
        self._attr_icon = SENSOR_ATTRIBUTES.get(key, {}).get("icon")
        self._attr_extra_state_attributes = {}

    async def async_update(self):
        data = await async_get_modem_data(self.url, self.username, self.password)
        values = data.get(self.key, [])
        if self.idx < len(values):
            self._attr_state = values[self.idx]
        else:
            self._attr_state = "unavailable"
        # Add all modem data as attributes, including the full list for this key
        self._attr_extra_state_attributes = {
            f"{self.key}_all": values,
            "channel_index": self.idx + 1,
            "total_channels": len(values),
            **{k: v for k, v in data.items() if k not in LIST_KEYS}
        }
