The below YAML's will get you to see all the data in one page. 

<img width="100%" alt="image" src="https://github.com/user-attachments/assets/9bf46e96-8544-40a8-a9c6-8f3c10c7fa17" />


## Event Log
```yaml
type: custom:flex-table-card
title: CM1200 Event Log
entities:
  include: sensor.cm1200_cable_modem_cm1200_cable_modem_cm1200_event_log
columns:
  - data: log.time
    name: Time
  - data: log.priority
    name: Priority
    modify: >-
          ( x == 1  || x == "Warning (5)" ? '<div style="color:orange;">' + x + '</div>' :"" 
          || x == "Notice (6)" ? '<div style="color:cornflowerblue;">' + x + '</div>' :"" 
          || x == "Critical (3)" ? '<div style="color:red;">' + x + '</div>' :""  
          || x == "Error (4)" ? '<div style="color:purple;">' + x + '</div>' :""
          )
  - data: log.description
    name: Description
max_rows: 50
sort_by: time
desc: true
```

## Starup Procedure

```yaml
type: custom:flex-table-card
entities:
  include: sensor.cm1200_cable_modem_cm1200_all_stats
columns:
  - data: system_uptime
    name: Uptime
  - data: boot_state, boot_comment, security_comment
    name: Status
  - data: downstream_channel_status, downstream_channel_comment
    name: Acquire Downstream Channel
```

## Downstream Bonded Channels

```yaml
type: custom:flex-table-card
title: CM1200 Downstream Bonded Channels
entities:
  include: sensor.cm1200_cable_modem_cm1200_ds_channel_*
columns:
  - data: channel
    name: Channel
  - data: lock_status
    name: Lock Status
  - data: modulation
    name: Modulation
  - data: channel_id
    name: Channel ID
  - data: frequency
    name: Frequency
  - data: power
    name: Power
  - data: snr
    name: SNR
  - data: correctables
    name: correctables
  - data: uncorrectables
    name: Uncorrectables
```

## Upstream Bonded Channels

```yaml
type: custom:flex-table-card
title: CM1200 Upstream Bonded Channels
entities:
  include: sensor.cm1200_cable_modem_cm1200_us_channel_*
columns:
  - data: channel
    name: Channel
  - data: lock_status
    name: Lock Status
  - data: us_channel_type
    name: US Channel Type
  - data: channel_id
    name: Channel ID
  - data: symbol_rate
    name: Symbol Rate
  - data: frequency
    name: Frequency
  - data: power
    name: Power
```

## Downstream OFDM Channels

```yaml
type: custom:flex-table-card
title: CM1200 Downstream OFDM Channels
entities:
  include: sensor.cm1200_cable_modem_cm1200_ofdm_channel*
columns:
  - data: channel
    name: Channel
  - data: lock_status
    name: Lock Status
  - data: modulation_/_profile_id
    name: Modulation / Profile ID
  - data: channel_id
    name: Channel ID
  - data: frequency
    name: Frequency
  - data: power
    name: Power
  - data: snr_/_mer
    name: SNR / MER
  - data: active_subcarrier_number_range
    name: Active Subcarrier Number Range
  - data: unerrored_codewords
    name: Unerrored Codewords
  - data: correctable_codewords
    name: Correctable Codewords
  - data: uncorrectable_codewords
    name: Uncorrectable Codewords
```
## Upstream OFDMA Channels

```yaml
type: custom:flex-table-card
title: CM1200 Upstream OFDMA Channels
entities:
  include: sensor.cm1200_cable_modem_cm1200_ofdma_channel*
columns:
  - data: channel
    name: Channel
  - data: lock_status
    name: Lock Status
  - data: modulation_/_profile_id
    name: Modulation / Profile ID
  - data: channel_id
    name: Channel ID
  - data: frequency
    name: Frequency
  - data: power
    name: Power
```

