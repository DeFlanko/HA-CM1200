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

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    url = config[CONF_URL]
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    scan_interval = config[CONF_SCAN_INTERVAL]

    sensors = [
        ModemScrapeSensor("Downstream Channel Frequency", url, username, password, "ds_frequencies"),
    ]
    async_add_entities(sensors, update_before_add=True)

class ModemScrapeSensor(SensorEntity):
    def __init__(self, name, url, username, password, key):
        self._attr_name = f"Modem {name}"
        self.url = url
        self.username = username
        self.password = password
        self.key = key
        self._attr_state = None

    async def async_update(self):
        data = await async_get_modem_data(self.url, self.username, self.password)
        self._attr_state = data.get(self.key, ["unavailable"])[0] if data.get(self.key) else "unavailable"
