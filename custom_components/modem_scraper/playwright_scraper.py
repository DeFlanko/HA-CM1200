import logging
from playwright.async_api import async_playwright

_LOGGER = logging.getLogger(__name__)

async def async_get_modem_data(url, username=None, password=None):
    data = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)

            # If your modem requires login, add selectors here.
            # (The HTML sample does not show a login form, so this is skipped.)

            # Wait for the main table populated by JS
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
            _LOGGER.error(f"Error scraping modem data: {e}")
        finally:
            await browser.close()
    return data
