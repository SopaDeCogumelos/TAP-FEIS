"""
Biblioteca Tuya para controle de dispositivos IoT

Esta biblioteca fornece classes para controle de dispositivos Tuya,
incluindo lâmpadas inteligentes e gerenciamento de dispositivos.
"""

from .smart_lamp import SmartLamp, load_device_config, find_device_by_name, get_dp_from_mapping
from .device_manager import DeviceManager
from .utils import clear_screen, format_status_readable, is_lamp_online

__version__ = "0.2.0"
__all__ = [
    "SmartLamp", "DeviceManager",
    "load_device_config", "find_device_by_name", "get_dp_from_mapping",
    "clear_screen", "format_status_readable", "is_lamp_online"
]