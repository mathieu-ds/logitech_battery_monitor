#!/usr/bin/env python3
"""
Logitech Battery Monitor
Reads LIVE battery data from G Hub Database
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import argparse


def get_ghub_data():
    """Read data from G Hub settings. db"""
    
    localappdata = os.environ.get('LOCALAPPDATA', '')
    db_path = Path(localappdata) / "LGHUB" / "settings.db"
    
    if not db_path.exists():
        return None
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT file FROM data WHERE _id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            if isinstance(row[0], bytes):
                json_str = row[0]. decode('utf-8')
            else:
                json_str = row[0]
            return json. loads(json_str)
        return None
        
    except Exception as e:
        print("Error: " + str(e))
        return None


def extract_battery_info(data):
    """Extract battery data - ONLY from /percentage nodes (live data)"""
    results = []
    
    if not data:
        return results
    
    # Device name mapping
    device_names = {
        'proxwirelessheadset': 'PRO X Wireless Gaming Headset',
        'prowirelessmouse': 'PRO Wireless Mouse',
        'gprowirelessmouse': 'G PRO Wireless Mouse',
        'g502lightspeed': 'G502 Lightspeed',
        'g915': 'G915 Keyboard',
        'g733': 'G733 Headset',
        'g435': 'G435 Headset',
        'g304': 'G304 Mouse',
        'g305': 'G305 Mouse',
        'g603': 'G603 Mouse',
        'g703': 'G703 Mouse',
        'g903': 'G903 Mouse',
    }
    
    for key, value in data.items():
        # ONLY process /percentage nodes - these have live data
        if key.startswith('battery/') and key.endswith('/percentage'):
            if isinstance(value, dict):
                parts = key.split('/')
                device_key = parts[1]
                
                # isCharging field: present and True = charging
                # isCharging field: absent = not charging
                is_charging = value.get('isCharging', False)
                
                device_info = {
                    'device': device_names.get(device_key, device_key),
                    'device_key': device_key,
                    'battery_percent': value.get('percentage'),
                    'voltage_mv': value.get('millivolts'),
                    'is_charging': is_charging,
                    'timestamp': value.get('time'),
                    'source': key,
                }
                
                # Only add if we have percentage
                if device_info['battery_percent'] is not None:
                    results.append(device_info)
    
    return results


def format_timestamp(timestamp):
    """Format ISO timestamp to readable format"""
    if not timestamp:
        return "N/A"
    
    try:
        ts = str(timestamp). replace('Z', '')
        if '+' in ts:
            ts = ts.split('+')[0]
        dt = datetime.fromisoformat(ts)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)


def print_batteries(batteries, as_json=False):
    """Print battery information"""
    
    if as_json:
        output = {
            'devices': batteries,
            'read_at': datetime.now(). isoformat(),
            'source': 'ghub_database'
        }
        print(json.dumps(output, indent=2))
        return
    
    if not batteries:
        print("")
        print("=" * 60)
        print("  NO LIVE BATTERY DATA AVAILABLE")
        print("=" * 60)
        print("")
        print("  Possible reasons:")
        print("  - G Hub is not running")
        print("  - Devices haven't reported battery recently")
        print("  - Use the device to trigger a battery update")
        print("")
        print("=" * 60)
        return
    
    print("")
    print("=" * 60)
    print("              LOGITECH BATTERY STATUS")
    print("=" * 60)
    
    for device in batteries:
        percent = device. get('battery_percent', 0)
        voltage = device.get('voltage_mv')
        is_charging = device. get('is_charging', False)
        timestamp = device.get('timestamp')
        source = device.get('source', '')
        
        # Battery bar
        filled = int(percent / 10)
        bar = "#" * filled + "-" * (10 - filled)
        
        # Status
        if is_charging:
            status = "CHARGING"
        elif percent >= 80:
            status = "Full"
        elif percent >= 50:
            status = "Good"
        elif percent >= 20:
            status = "Medium"
        else:
            status = "LOW!"
        
        print("")
        print("  " + device['device'])
        print("  " + "-" * 56)
        print("    Battery:    [" + bar + "] " + str(percent) + "%")
        print("    Status:     " + status)
        
        if voltage:
            print("    Voltage:    " + str(voltage) + " mV")
        else:
            print("    Voltage:    N/A")
        
        if is_charging:
            print("    Charging:   YES [+]")
        else:
            print("    Charging:   No")
        
        print("    Updated:    " + format_timestamp(timestamp))
        print("    Source:     " + source)
    
    print("")
    print("  " + "-" * 56)
    print("  Read at: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    print("")


def main():
    parser = argparse.ArgumentParser(description="Logitech Battery Monitor")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--loop", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=30, help="Update interval (seconds)")
    args = parser.parse_args()
    
    if args.loop:
        print("Logitech Battery Monitor - Ctrl+C to stop")
        print("Reading live data from G Hub database...")
        print("")
        
        import time
        try:
            while True:
                data = get_ghub_data()
                batteries = extract_battery_info(data)
                
                # Clear screen
                print("\033[H\033[J", end="")
                print_batteries(batteries, as_json=args. json)
                
                time.sleep(args. interval)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        data = get_ghub_data()
        batteries = extract_battery_info(data)
        print_batteries(batteries, as_json=args.json)


if __name__ == "__main__":
    main()