# Home Assistant Modem Scraper Integration

This custom integration uses [Playwright](https://playwright.dev/python/) to scrape data from a JavaScript-rendered cable modem status page and exposes it as Home Assistant sensors.

## Features

- Runs a headless Chromium browser to load and scrape modem data after JS is rendered.
- Exposes sensors for desired modem status points.
- Easy to extend with new selectors.

## Installation

1. Copy the `custom_components/modem_scraper/` directory into your Home Assistant `custom_components/` folder.
2. Install Playwright and browser binaries in your Home Assistant environment:
    ```bash
    pip install playwright
    playwright install chromium
    ```
   (You may need to do this inside your Home Assistant container or virtualenv. For Home Assistant OS or Supervised, use a separate system and send results via MQTT or REST.)
3. Restart Home Assistant.

## Configuration

Example in `configuration.yaml`:
```yaml
sensor:
  - platform: modem_scraper
    url: "http://192.168.100.1/DocsisStatus.htm"
    username: "your_user"   # Optional, only if your modem requires login
    password: "your_password"
    scan_interval: 300      # Optional, seconds between scrapes
```

## Adding/Modifying Selectors

Edit `playwright_scraper.py` to change what data is scraped and exposed.

## Troubleshooting

- If you see errors about missing Playwright or browser binaries, ensure step 2 above was completed successfully in your Python environment.
- This integration is best for Home Assistant Core or Container installs. Home Assistant OS/Supervised users may need to run scraping on another system and push data in via MQTT.

## License

MIT
