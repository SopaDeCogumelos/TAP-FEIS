"""
Módulo para gerenciar dispositivos compatíveis com a plataforma Tuya.
Baseado no template de controle da Tuya para lâmpadas RGB inteligentes.
"""

import tinytuya as tuya
import json
from base_device import Device


class TuyaDevice(Device):
    """
    Classe para representar um dispositivo compatível com Tuya, como uma lâmpada inteligente.
    Herda da classe base 'Device'.
    
    Controles disponíveis (Data Points):
    - DP 20: switch_led (Boolean) - Liga/desliga
    - DP 21: work_mode (Enum) - Modo: white, colour, scene, music
    - DP 22: bright_value_v2 (Integer 10-1000) - Brilho
    - DP 23: temp_value_v2 (Integer 0-1000) - Temperatura de cor
    - DP 24: colour_data_v2 (JSON HSV) - Dados de cor HSV
    """
    
    # Mapeamento de DPs
    DP_SWITCH = '20'
    DP_MODE = '21'
    DP_BRIGHTNESS = '22'
    DP_COLOR_TEMP = '23'
    DP_COLOR_DATA = '24'
    
    # Modos disponíveis
    MODE_WHITE = 'white'
    MODE_COLOR = 'colour'
    MODE_SCENE = 'scene'
    MODE_MUSIC = 'music'
    
    def __init__(self, name, dev_id, address, local_key, status="unknown"):
        """
        Inicializa o dispositivo Tuya.
        """
        super().__init__(name, "tuya_lamp", status)
        
        self.dev_id = dev_id
        self.address = address
        self.local_key = local_key
        
        # Inicializa o objeto do dispositivo
        self.device = tuya.BulbDevice(dev_id, address, local_key)
        self.device.set_version(3.3)
        
        # Tenta obter o status inicial
        try:
            initial_status = self.device.status()
            if initial_status and 'dps' in initial_status:
                if self.DP_SWITCH in initial_status['dps']:
                    self.status = "on" if initial_status['dps'][self.DP_SWITCH] else "off"
                print(f"  - '{name}' inicializado. Status: {self.status}")
        except Exception as e:
            print(f"  - AVISO ao inicializar '{name}': {e}")
            self.status = "unknown"

    def _send_command(self, dp, value):
        """
        Envia um comando para um Data Point específico.
        """
        try:
            result = self.device.set_value(dp, value)
            return True, result
        except Exception as e:
            return False, str(e)

    def _get_status(self):
        """
        Obtém o status atual de todos os data points.
        """
        try:
            status = self.device.status()
            if status and 'dps' in status:
                return status['dps']
            return None
        except Exception as e:
            print(f"ERRO ao obter status de '{self.name}': {e}")
            return None

    def turn_on(self):
        """
        Liga a lâmpada.
        """
        success, msg = self._send_command(self.DP_SWITCH, True)
        if success:
            self.status = "on"
            return True, f"'{self.name}' ligada com sucesso."
        else:
            return False, f"ERRO ao ligar '{self.name}': {msg}"

    def turn_off(self):
        """
        Desliga a lâmpada.
        """
        success, msg = self._send_command(self.DP_SWITCH, False)
        if success:
            self.status = "off"
            return True, f"'{self.name}' desligada com sucesso."
        else:
            return False, f"ERRO ao desligar '{self.name}': {msg}"

    def toggle(self):
        """
        Alterna entre ligado e desligado.
        """
        dps = self._get_status()
        if dps and self.DP_SWITCH in dps:
            current = dps[self.DP_SWITCH]
            return self.turn_on() if not current else self.turn_off()
        else:
            return False, f"ERRO ao alternar '{self.name}': não conseguiu obter status"

    def set_brightness(self, brightness):
        """
        Ajusta o brilho (10-1000).
        """
        # Primeiro, muda para modo "white"
        success_mode, msg_mode = self._send_command(self.DP_MODE, self.MODE_WHITE)
        if not success_mode:
            return False, f"ERRO ao mudar modo para white: {msg_mode}"
        
        # Converte se passou um valor em porcentagem (0-100)
        if brightness <= 100:
            brightness = int((brightness / 100) * 1000)
        
        brightness = max(10, min(1000, brightness))
        
        success, msg = self._send_command(self.DP_BRIGHTNESS, brightness)
        if success:
            return True, f"Brilho de '{self.name}' ajustado para {brightness}/1000."
        else:
            return False, f"ERRO ao ajustar brilho: {msg}"

    def set_color_temp(self, temp):
        """
        Ajusta a temperatura de cor (0-1000).
        """
        # Primeiro, muda para modo "white"
        success_mode, msg_mode = self._send_command(self.DP_MODE, self.MODE_WHITE)
        if not success_mode:
            return False, f"ERRO ao mudar modo para white: {msg_mode}"
        
        # Converte se passou um valor em porcentagem (0-100)
        if temp <= 100:
            temp = int((temp / 100) * 1000)
        
        temp = max(0, min(1000, temp))
        
        success, msg = self._send_command(self.DP_COLOR_TEMP, temp)
        if success:
            return True, f"Temperatura de cor de '{self.name}' ajustada para {temp}/1000."
        else:
            return False, f"ERRO ao ajustar temperatura: {msg}"

    def set_color(self, h, s=None, v=None):
        """
        Ajusta a cor usando HSV.
        """
        if s is None:
            s = 1000
        if v is None:
            v = 1000
        
        h = max(0, min(360, h))
        s = max(0, min(1000, s))
        v = max(10, min(1000, v))
        
        # Muda para modo "colour"
        success_mode, msg_mode = self._send_command(self.DP_MODE, self.MODE_COLOR)
        if not success_mode:
            return False, f"ERRO ao mudar modo para colour: {msg_mode}"
        
        # Envia dados de cor
        color_data = {"h": h, "s": s, "v": v}
        success, msg = self._send_command(self.DP_COLOR_DATA, json.dumps(color_data))
        if success:
            return True, f"Cor de '{self.name}' ajustada para HSV({h}°, {s}, {v})."
        else:
            return False, f"ERRO ao ajustar cor: {msg}"

    def set_rgb(self, r, g, b):
        """
        Ajusta a cor usando RGB (0-255).
        """
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        h, s, v = self._rgb_to_hsv(r, g, b)
        return self.set_color(h, s, v)

    def set_mode(self, mode):
        """
        Muda o modo de funcionamento.
        """
        valid_modes = [self.MODE_WHITE, self.MODE_COLOR, self.MODE_SCENE, self.MODE_MUSIC]
        if mode not in valid_modes:
            return False, f"Modo inválido. Modos: {', '.join(valid_modes)}"
        
        success, msg = self._send_command(self.DP_MODE, mode)
        if success:
            return True, f"Modo de '{self.name}' alterado para '{mode}'."
        else:
            return False, f"ERRO ao alterar modo: {msg}"

    def get_status(self):
        """
        Retorna o status atual de todos os data points.
        """
        dps = self._get_status()
        if not dps:
            return {"error": "Não foi possível obter status"}
        
        status_info = {
            "power": "on" if dps.get(self.DP_SWITCH) else "off",
            "mode": dps.get(self.DP_MODE, "unknown"),
            "brightness": dps.get(self.DP_BRIGHTNESS, "unknown"),
            "color_temp": dps.get(self.DP_COLOR_TEMP, "unknown"),
            "raw_dps": dps
        }
        return status_info

    def to_dict(self):
        """
        Converte os atributos para um dicionário.
        """
        base_dict = super().to_dict()
        base_dict.update({
            "dev_id": self.dev_id,
            "address": self.address,
            "local_key": self.local_key
        })
        return base_dict

    @staticmethod
    def scan_devices():
        """
        Procura por dispositivos Tuya na rede local.
        """
        print("Procurando por dispositivos Tuya na rede...")
        try:
            devices = tuya.deviceScan()
            return devices
        except Exception as e:
            print(f"ERRO ao procurar dispositivos: {e}")
            return {}

    @staticmethod
    def _rgb_to_hsv(r, g, b):
        """
        Converte RGB (0-255) para HSV.
        Retorna (h, s, v) onde h é 0-360, s e v são 0-1000.
        """
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        
        max_c = max(r_norm, g_norm, b_norm)
        min_c = min(r_norm, g_norm, b_norm)
        delta = max_c - min_c
        
        if delta == 0:
            h = 0
        elif max_c == r_norm:
            h = 60 * (((g_norm - b_norm) / delta) % 6)
        elif max_c == g_norm:
            h = 60 * (((b_norm - r_norm) / delta) + 2)
        else:
            h = 60 * (((r_norm - g_norm) / delta) + 4)
        
        s = 0 if max_c == 0 else (delta / max_c)
        v = max_c
        
        h = int(h) % 360
        s = int(s * 1000)
        v = int(v * 1000)
        
        return h, s, v
        return base_dict
