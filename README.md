# Logitech Battery Monitor

A Python script to read battery status from Logitech wireless devices (headsets, mice, keyboards) by accessing the Logitech G Hub database.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

---

## Table of Contents

1. [Features](#features)
2. [Supported Devices](#supported-devices)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Output Formats](#output-formats)
7. [How It Works](#how-it-works)
8. [Database Structure](#database-structure)
9. [Integration Examples](#integration-examples)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

---

## Features

- ✅ **Accurate battery percentage** - Reads the exact value shown in G Hub
- ✅ **Voltage monitoring** - Shows battery voltage in millivolts
- ✅ **Charging detection** - Detects when device is charging
- ✅ **Multiple devices** - Supports all Logitech wireless devices managed by G Hub
- ✅ **JSON output** - Easy integration with other tools and APIs
- ✅ **No G Hub interference** - Works while G Hub is running
- ✅ **No dependencies** - Uses only Python standard library

---

## Supported Devices

| Device Type | Examples |
|-------------|----------|
| Headsets | PRO X Wireless, G733, G435 |
| Mice | PRO Wireless, G502 Lightspeed, G703, G903, G304, G305 |
| Keyboards | G915, G815 |

> Any wireless device managed by Logitech G Hub should work. 

---

## Requirements

- **Windows 10/11**
- **Python 3.7+**
- **Logitech G Hub** (installed and running)

---

## Installation

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/logitech_battery_monitor.git
cd logitech_battery_monitor
```

Or download `logitech_battery_final.py` directly. 

### 2.  Create Virtual Environment (Optional)

```bash
python -m venv . venv
. venv\Scripts\activate
```

### 3. No Dependencies Required! 

The script uses only Python standard library modules:
- `sqlite3`
- `json`
- `os`
- `pathlib`
- `datetime`
- `argparse`

---

## Usage

### Basic Usage

```bash
python logitech_battery_final.py
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--json` | Output in JSON format | Disabled |
| `--loop` | Continuous monitoring mode | Disabled |
| `--interval <seconds>` | Update interval for loop mode | 30 |

### Examples

```bash
# Single reading
python logitech_battery_final. py

# JSON output (for API/scripts)
python logitech_battery_final.py --json

# Continuous monitoring every 30 seconds
python logitech_battery_final.py --loop

# Continuous monitoring every 10 seconds
python logitech_battery_final.py --loop --interval 10
```

---

## Output Formats

### Console Output

```
============================================================
              LOGITECH BATTERY STATUS
============================================================

  PRO X Wireless Gaming Headset
  --------------------------------------------------------
    Battery:    [#########-] 91%
    Status:     CHARGING
    Voltage:    4017 mV
    Charging:   YES [+]
    Updated:    2025-11-28 22:17:51
    Source:     battery/proxwirelessheadset/percentage

  PRO Wireless Mouse
  --------------------------------------------------------
    Battery:    [########--] 87%
    Status:     Full
    Voltage:    4044 mV
    Charging:   No
    Updated:    2025-11-28 22:12:08
    Source:     battery/prowirelessmouse/percentage

  --------------------------------------------------------
  Read at: 2025-11-28 23:20:00
============================================================
```

### JSON Output

```json
{
  "devices": [
    {
      "device": "PRO X Wireless Gaming Headset",
      "device_key": "proxwirelessheadset",
      "battery_percent": 91,
      "voltage_mv": 4017,
      "is_charging": true,
      "timestamp": "2025-11-28T22:17:51Z",
      "source": "battery/proxwirelessheadset/percentage"
    },
    {
      "device": "PRO Wireless Mouse",
      "device_key": "prowirelessmouse",
      "battery_percent": 87,
      "voltage_mv": 4044,
      "is_charging": false,
      "timestamp": "2025-11-28T22:12:08Z",
      "source": "battery/prowirelessmouse/percentage"
    }
  ],
  "read_at": "2025-11-28T23:20:00. 000000",
  "source": "ghub_database"
}
```

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Logitech Wireless Device                     │
│                 (PRO X Headset, PRO Mouse, etc.)                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ USB / Lightspeed / Bluetooth
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Logitech G Hub                             │
│                   (Windows Application)                         │
│                                                                 │
│  - Communicates with devices via HID++ protocol                 │
│  - Polls battery status periodically (~2 minutes)               │
│  - Stores data in SQLite database                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Writes to
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      settings.db                                │
│           %LOCALAPPDATA%\LGHUB\settings.db                      │
│                                                                 │
│  SQLite database containing:                                    │
│  - Device configurations                                        │
│  - Battery status (live data)                                   │
│  - User preferences                                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Reads from
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  logitech_battery_final.py                      │
│                    (This Script)                                │
│                                                                 │
│  - Opens SQLite database (read-only)                            │
│  - Extracts JSON blob from 'data' table                         │
│  - Parses battery information                                   │
│  - Outputs to console or JSON                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         START                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Read %LOCALAPPDATA%\LGHUB\settings.db                          │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Execute: SELECT file FROM data WHERE _id = 1                   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Decode BLOB as UTF-8 → Parse as JSON                           │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Find keys matching: battery/*/percentage                       │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  For each matching key:                                         │
│    - Extract: percentage, millivolts, isCharging, time          │
│    - Map device_key to friendly name                            │
│    - Add to results list                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Output results (Console or JSON)                               │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  If --loop: wait interval, repeat                               │
│  Else: END                                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Structure

### Database Location

```
%LOCALAPPDATA%\LGHUB\settings.db
```

Typically resolves to:
```
C:\Users\<USERNAME>\AppData\Local\LGHUB\settings.db
```

### Database Schema

| Table | Description |
|-------|-------------|
| `data` | Main configuration and state data |
| `snapshots` | Profile snapshots (not used for battery) |

#### `data` Table

| Column | Type | Description |
|--------|------|-------------|
| `_id` | INTEGER | Primary key (always 1) |
| `_date_created` | DATETIME | Last update timestamp |
| `file` | BLOB | JSON data (UTF-8 encoded) |

### JSON Structure

The `file` column contains a JSON object with flat keys using `/` as separator:

```json
{
  "battery/prowirelessmouse/percentage": {
    "millivolts": 4044,
    "percentage": 87,
    "time": "2025-11-28T22:12:08Z"
  },
  "battery/proxwirelessheadset/percentage": {
    "isCharging": true,
    "millivolts": 4017,
    "percentage": 91,
    "time": "2025-11-28T22:17:51Z"
  }
}
```

### Battery Data Fields

**Key Pattern:** `battery/<device_key>/percentage`

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `percentage` | Integer | Battery level (0-100) | `91` |
| `millivolts` | Integer | Battery voltage in mV | `4017` |
| `isCharging` | Boolean | Charging status (only present when `true`) | `true` |
| `time` | String | ISO 8601 timestamp of last update | `"2025-11-28T22:17:51Z"` |

### Charging Status Behavior

The `isCharging` field has special behavior:

```
When CHARGING:
{
  "isCharging": true,    ← Field is PRESENT
  "millivolts": 4017,
  "percentage": 91,
  "time": "2025-11-28T22:17:51Z"
}

When NOT CHARGING:
{
                         ← Field is ABSENT (not false!)
  "millivolts": 4153,
  "percentage": 91,
  "time": "2025-11-28T22:18:01Z"
}
```

> **Note:** The script interprets a missing `isCharging` field as "not charging". 

---

## Integration Examples

### Send to Raspberry Pi

```python
import requests
import subprocess
import json

# Run the script and capture JSON output
result = subprocess.run(
    ['python', 'logitech_battery_final.py', '--json'],
    capture_output=True,
    text=True
)

batteries = json.loads(result.stdout)

# Send to Raspberry Pi
RASPBERRY_PI_URL = "http://192.168.1.100:5000/battery"
response = requests.post(RASPBERRY_PI_URL, json=batteries)
print("Sent to Pi:", response.status_code)
```

### Windows Task Scheduler

Run every 5 minutes and log to file:

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "C:\path\to\logitech_battery_final.py --json >> C:\logs\battery.log"

$trigger = New-ScheduledTaskTrigger `
    -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask `
    -TaskName "LogitechBatteryMonitor" `
    -Action $action `
    -Trigger $trigger
```

### Home Assistant Integration

Use the JSON output with a command line sensor:

```yaml
sensor:
  - platform: command_line
    name: Logitech Headset Battery
    command: 'python /path/to/logitech_battery_final.py --json'
    value_template: '{{ value_json.devices[0].battery_percent }}'
    unit_of_measurement: '%'
    json_attributes:
      - devices
    scan_interval: 300
```

### PowerShell Script

```powershell
# Get battery status as PowerShell object
$battery = python logitech_battery_final.py --json | ConvertFrom-Json

foreach ($device in $battery.devices) {
    Write-Host "$($device.device): $($device.battery_percent)%"
    
    if ($device.battery_percent -lt 20) {
        # Send notification
        [System.Windows.MessageBox]::Show(
            "$($device.device) battery is low: $($device.battery_percent)%",
            "Low Battery Warning"
        )
    }
}
```

---

## Troubleshooting

### No Battery Data Found

| Cause | Solution |
|-------|----------|
| G Hub not installed | Install Logitech G Hub |
| G Hub not running | Start Logitech G Hub application |
| Device in sleep mode | Move mouse or use headset to wake device |
| Device just connected | Wait 1-2 minutes for G Hub to poll battery |
| No recent update | Force disconnect/reconnect of the device |

**Check database exists:**
```powershell
Test-Path "$env:LOCALAPPDATA\LGHUB\settings.db"
```

### Database Locked Error

**Error:** `database is locked`

**Cause:** G Hub is writing to the database

**Solution:** The script uses read-only access, simply retry after a moment

---

## Limitations

| Limitation | Details |
|------------|---------|
| G Hub dependency | G Hub must be installed and running |
| Update frequency | Battery data updates every ~2 minutes (G Hub limitation) |
| Windows only | Database location is Windows-specific |
| No real-time data | Data is as fresh as G Hub's last poll |

---

## Adding New Devices

To add support for a new device, add its key to the `device_names` dictionary in the script:

```python
device_names = {
    'proxwirelessheadset': 'PRO X Wireless Gaming Headset',
    'prowirelessmouse': 'PRO Wireless Mouse',
    'yournewdevice': 'Your New Device Name',  # Add here
    # ... 
}
```

The device key can be found by checking G Hub's database for `battery/*/percentage` keys.
