# AI Agent Instructions for TAP-FEIS Project

## Project Overview
**Projeto Final - Gerenciamento de Dispositivos IoT Tuya**

A Python application for controlling Tuya smart lamps with an interactive CLI interface. Implements device discovery, local control via Tuya protocol v3.5, and persistent device management.

**Key Technologies:** Python 3.x, tinytuya library, Tuya Local Protocol, JSON configuration

---

## Architecture Patterns

### 1. **Core Component: SmartLamp Class** (`main.py:46-250`)
- **Purpose:** High-level wrapper around tinytuya.BulbDevice
- **Key Pattern:** Encapsulates protocol details (DP mapping) from UI
- **Data Points (DP) Mapping:**
  - DP20: switch_led (on/off)
  - DP21: work_mode (white/colour/scene/music)
  - DP22: bright_value (brightness 0-1000)
  - DP23: temp_value (temperature 0-1000)
  - DP24: colour_data (color in HSV format)

**Usage:**
```python
lamp = SmartLamp(device_config, version=3.5)
if lamp.connect(timeout=5):
    lamp.set_brightness(50)  # Percentage 0-100
    lamp.set_color_rgb(255, 0, 0)  # Use set_colour() internally
```

### 2. **Device Management: DeviceManager Class** (`device_manager.py:11-446`)
- **Purpose:** Persistent device storage, discovery, import/export
- **Files Managed:**
  - `devices.json`: Custom format (our schema)
  - `tinytuya.json`: tinytuya discovery output
  - `tuya-raw.json`: Raw discovery data
  - `backup_YYYYMMDD_HHMMSS/`: Auto-backups before operations

**Key Operations:**
```python
manager = DeviceManager('devices.json', 'tinytuya.json', 'tuya-raw.json')
manager.load_devices()  # Load from disk
manager.add_device()    # CLI-driven manual entry
manager.backup_files()  # Auto-backup before changes
```

### 3. **UI Architecture: Menu-Driven CLI** (`main.py:815-1029`)
- **Entry Point:** `main()` → Menu selection → `control_lamp()` or `admin_menu()`
- **Pattern:** Each menu function handles user input and calls appropriate action
- **Clear Screen:** `os.system('cls')` on Windows, `clear` on Linux

**Menu Hierarchy:**
```
main() [Menu 1: Control/Admin]
├─ control_lamp() [Menu 2: Lamp Selection]
│  └─ interactive_menu() [Menu 3: Lamp Control]
│     ├─ toggle_power()
│     ├─ set_brightness()
│     ├─ set_temperature()
│     ├─ set_color() [Submenu: Hex/RGB/Preset]
│     ├─ show_status()
│     ├─ show_debug_menu() [Submenu: Info/TestSequence]
│     └─ [Option 7: Switch lamp]
└─ admin_menu() [Device Management]
   ├─ discover_devices() [tinytuya.discover()]
   ├─ add_device() [Manual CLI entry]
   ├─ list_devices()
   ├─ edit_device()
   └─ [Other CRUD operations]
```

---

## Critical Developer Workflows

### Running the Application
```bash
cd Projeto/v0.2
python main.py
```

### Testing Device Discovery
```python
# Direct discovery (used in admin_menu):
import tinytuya
discovered = tinytuya.discover()  # Returns dict of devices on network
```

### Device Configuration Flow
1. **Initial:** Run wizard via CLI (Menu 2 → Option 1)
2. **Discovery:** `tinytuya.discover()` finds devices with IP
3. **Sync:** Results merged into `devices.json` with deduplication
4. **Manual:** CLI prompts for Device ID, Local Key, IP (optional)

### Error Handling Pattern
```python
# Connection failures return False, suggest troubleshooting:
if not lamp.connect(timeout=5):
    print("Timeout: Device offline?")
    print("Suggest: Configure IP in device_manager")
    retry = input("🔄 Try again? (s/n): ")
```

---

## Project-Specific Conventions

### 1. **Device Configuration Schema** (`devices.json`)
```json
{
  "id": "ebecbc6d2743ca812dzudh",
  "name": "Quarto Frente",
  "key": "SJ*:Nn{{+VN2kH3^",      // Local authentication key
  "ip": "192.168.1.6",             // Optional - required for speed
  "mac": "18:de:50:05:6b:e1",     // For reference
  "uuid": "66d3673805254b5e",     // For reference
  "model": "10W",                  // For reference
  "mapping": {}                    // Protocol DP mappings (optional)
}
```

### 2. **Percentage Conversion**
- **Brightness/Temperature:** Always UI uses 0-100%, internally converted:
  ```python
  # SmartLamp converts automatically via tinytuya methods:
  device.set_brightness_percentage(50)      # 0-100
  device.set_colourtemp_percentage(50)      # 0-100
  ```

### 3. **Status Display Formatting** (`format_status_readable()`)
- Converts raw DPS values to human-readable format
- Shows: On/Off, Mode, Brightness %, Temperature %, Color hex

### 4. **Timeout Handling**
- Default: 5 seconds for connections
- 3 seconds for discovery checks
- Always specify in `connect(timeout=5)`

### 5. **Error Messages**
- Use emoji for visual hierarchy:
  - ✓ Success (green)
  - ✗ Error (red)
  - ⚠️ Warning (yellow)
  - 🔄 Retry prompt

---

## Integration Points & External Dependencies

### tinytuya Library
- **Version:** 1.x (compatible with Tuya Protocol 3.5)
- **Key Methods Used:**
  - `tinytuya.BulbDevice()` - Device connection
  - `tinytuya.discover()` - Find devices on network
  - `.status()` - Get device state
  - `.set_value(dp, value)` - Low-level control
  - `.set_brightness_percentage(0-100)` - High-level brightness
  - `.set_colour(r,g,b)` - Color control

### Tuya Cloud API
- **Purpose:** Obtain Local Authentication Key
- **Required for:** Adding devices manually
- **Documentation:** See `OBTER_CHAVE_LOCAL.md`

### File System
- **Current Directory:** All JSON files stored relative to script
- **Backups:** Create timestamped directories, not files
- **Encoding:** Always UTF-8 for JSON (handles device names with accents)

---

## Common Modifications & Extension Points

### Adding New Lamp Control Feature
1. Add method to `SmartLamp` class (e.g., `set_scene()`)
2. Create UI function in menu section (e.g., `select_scene()`)
3. Add to `menu_options` dict in `interactive_menu()` with new option number
4. Update `print_menu()` to show new option

### Adding Device Import Source
- Extend `DeviceManager.import_devices()` to parse new format
- Example: CSV, YAML, or cloud API export
- Ensure deduplication logic (check `device['id']` exists)

### Customizing Status Display
- Edit `format_status_readable()` function (~350 lines)
- Add new DPs or formatting logic
- Example: Add scene_data display if available

---

## Troubleshooting Guide for Agents

### Issue: `tinytuya.discover()` returns empty
- **Cause:** Device offline or on different network
- **Fix:** Verify IP manually in device config, use IP instead of discovery

### Issue: Connection timeout on device with IP
- **Cause:** Device offline or port blocked
- **Fix:** Increase timeout parameter or check device is powered on

### Issue: Color not updating
- **Cause:** Using `set_value()` instead of `set_colour()`
- **Fix:** Always use high-level methods in SmartLamp class

### Issue: Import fails with "duplicate"
- **Cause:** Device ID already in `devices.json`
- **Fix:** Edit existing device or manually remove duplicate

---

## File Dependency Map

```
main.py (1029 lines)
├─ imports: device_manager.DeviceManager
├─ SmartLamp class (encapsulates tinytuya.BulbDevice)
├─ UI functions (menus, prompts, display)
└─ Entry point: main() → control_lamp() or admin_menu()

device_manager.py (446 lines)
├─ DeviceManager class
├─ Uses: tinytuya.discover() for discovery
├─ Manages: devices.json, tinytuya.json, tuya-raw.json
└─ Operations: CRUD, backup, import/export

devices.json
├─ Source: Manual entry or tinytuya.discover()
├─ Format: List of device dicts
└─ Used by: SmartLamp, select_lamp_menu()

GERENCIAMENTO.md
└─ User documentation (not code)
```

---

## Before Making Changes

- **Always check** if modification affects both `SmartLamp` and `DeviceManager`
- **Test connection** with both online and offline devices
- **Verify** new code handles empty/missing device configs gracefully
- **Update** menu option numbers consistently across print_menu() and menu_options dict
- **Preserve** UTF-8 encoding in file I/O

