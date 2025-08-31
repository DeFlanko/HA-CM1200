@echo off
start "" cmd /k "python C:\CM1200\cm1200_mqtt_discovery_scraper.py > C:\CM1200\details_log.log 2>&1"
start "" cmd /k "python C:\CM1200\cm1200_mqtt_eventlog_scraper.py > C:\CM1200\event_log.log 2>&1"
