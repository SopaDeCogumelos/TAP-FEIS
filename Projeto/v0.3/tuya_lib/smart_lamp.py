"""
Módulo SmartLamp - Controle de lâmpadas inteligentes Tuya

Este módulo contém a classe SmartLamp para controle de dispositivos
de iluminação Tuya através do protocolo local.
"""

import json
import time
import tinytuya
import os
import socket


"""
===================
BEGIN Declaração de classes
===================
"""

"""
BEGIN SmartLamp
 - @param device_config : Dicionário com configurações do dispositivo (id, name, key, ip, etc.)
 - @param version : Versão do protocolo Tuya (padrão 3.5)
 - @var/obj config : Configurações do dispositivo
 - @var/obj version : Versão do protocolo Tuya
 - @var/obj device : Instância do BulbDevice do tinytuya
 - @var/obj connected : Status de conexão (True/False)
 - @var/obj dp_switch : Data Point para controle liga/desliga
 - @var/obj dp_brightness : Data Point para controle de brilho
 - @var/obj dp_work_mode : Data Point para modo de trabalho
 - @var/obj dp_colour : Data Point para dados de cor
 - @var/obj dp_temperature : Data Point para temperatura da cor
 - @method connect : Conecta ao dispositivo Tuya
 - @method get_status : Obtém status atual do dispositivo
 - @method turn_on : Liga a lâmpada
 - @method turn_off : Desliga a lâmpada
 - @method set_brightness : Define brilho da lâmpada (0-100%)
 - @method set_work_mode : Define modo de trabalho (white/colour/scene/music)
 - @method set_color_hex : Define cor por código hexadecimal
 - @method set_color_rgb : Define cor por valores RGB
 - @method set_temperature : Define temperatura da cor (0-100%)
 - @method get_info : Retorna informações formatadas da lâmpada
 - @retparms : Instância da classe SmartLamp
"""
class SmartLamp:
    """Classe para controlar uma lâmpada Tuya"""

    def __init__(self, device_config: dict, version: float = 3.5):
        """
        Inicializa a lâmpada com as configurações do dispositivo

        Args:
            device_config: Dicionário com configurações do dispositivo
            version: Versão do protocolo Tuya (padrão 3.5)
        """
        self.config = device_config
        self.version = version
        self.device = None
        self.connected = False

        # Extrai DPs importantes (com fallback para padrão)
        self.dp_switch = get_dp_from_mapping(device_config, 'switch_led') or '20'
        self.dp_brightness = get_dp_from_mapping(device_config, 'bright_value') or '22'
        self.dp_work_mode = get_dp_from_mapping(device_config, 'work_mode') or '21'
        self.dp_colour = get_dp_from_mapping(device_config, 'colour_data') or '24'
        self.dp_temperature = get_dp_from_mapping(device_config, 'temp_value') or '23'

    def connect(self, timeout: int = 5) -> bool:
        """
        Conecta ao dispositivo com timeout

        Args:
            timeout: Tempo máximo de espera em segundos
        """
        try:
            # Verifica se tem IP definido
            address = self.config.get('ip', '').strip()
            if not address:
                # Se não tem IP, tenta usar scan (será lento em dispositivos offline)
                address = 'scan'

            # Usa BulbDevice ao invés de OutletDevice para ter acesso aos métodos de cor
            self.device = tinytuya.BulbDevice(
                dev_id=self.config['id'],
                address=address,
                local_key=self.config['key'],
                version=self.version,
                connection_timeout=timeout  # Define timeout de conexão
            )

            # Define timeout também para operações
            self.device.set_socketTimeout(timeout)

            # Tenta obter status para verificar conexão
            status = self.device.status()

            if status is None or 'Error' in str(status):
                print(f"Erro: Dispositivo retornou: {status}")
                self.connected = False
                return False

            self.connected = True
            return True

        except socket.timeout:
            device_ip = self.config.get('ip', 'desconhecido')
            print(f"⏱️  Timeout: Dispositivo em {device_ip} não responde (offline?)")
            self.connected = False
            return False
        except ConnectionRefusedError:
            device_ip = self.config.get('ip', 'desconhecido')
            print(f"🚫 Conexão recusada: Dispositivo em {device_ip} (offline?)")
            self.connected = False
            return False
        except RuntimeError as e:
            error_msg = str(e)
            if "Unable to find device" in error_msg:
                device_ip = self.config.get('ip', 'scan')
                print(f"🔍 Não encontrado: Dispositivo não está acessível (offline?)")
                print(f"   IP configurado: {device_ip if device_ip else '(nenhum, tentando scan)'}")
                self.connected = False
                return False
            else:
                print(f"Erro: {e}")
                self.connected = False
                return False
        except Exception as e:
            print(f"Erro ao conectar: {type(e).__name__}: {e}")
            self.connected = False
            return False

    def get_status(self) -> dict:
        """Retorna o status atual do dispositivo"""
        if not self.connected or not self.device:
            return None

        try:
            return self.device.status()
        except Exception as e:
            print(f"Erro ao obter status: {e}")
            return None

    def turn_on(self) -> bool:
        """Liga a lâmpada"""
        if not self.connected or not self.device:
            print("Dispositivo não conectado!")
            return False

        try:
            result = self.device.set_value(self.dp_switch, True)
            return 'Error' not in str(result)
        except Exception as e:
            print(f"Erro ao ligar: {e}")
            return False

    def turn_off(self) -> bool:
        """Desliga a lâmpada"""
        if not self.connected or not self.device:
            print("Dispositivo não conectado!")
            return False

        try:
            result = self.device.set_value(self.dp_switch, False)
            return 'Error' not in str(result)
        except Exception as e:
            print(f"Erro ao desligar: {e}")
            return False

    def set_brightness(self, value: int) -> bool:
        """
        Define o brilho da lâmpada usando porcentagem

        Args:
            value: Valor de brilho em porcentagem (0-100)
        """
        if not self.connected or not self.device:
            print("Dispositivo não conectado!")
            return False

        # Valida o intervalo (0-100%)
        value = max(0, min(100, value))

        print(f"DEBUG: Configurando brilho para {value}%")

        try:
            # Usa set_brightness_percentage do BulbDevice
            result = self.device.set_brightness_percentage(value, nowait=False)
            print(f"DEBUG: Resultado: {result}")
            return 'Error' not in str(result)
        except Exception as e:
            print(f"Erro ao ajustar brilho: {e}")
            import traceback
            traceback.print_exc()
            return False

    def set_work_mode(self, mode: str) -> bool:
        """
        Define o modo de trabalho

        Args:
            mode: 'white', 'colour', 'scene' ou 'music'
        """
        if not self.connected or not self.device:
            print("Dispositivo não conectado!")
            return False

        valid_modes = ['white', 'colour', 'scene', 'music']
        if mode not in valid_modes:
            print(f"Modo inválido! Modos válidos: {', '.join(valid_modes)}")
            return False

        print(f"DEBUG: Mudando para modo '{mode}'")

        try:
            # Usa set_mode do BulbDevice
            result = self.device.set_mode(mode, nowait=False)
            print(f"DEBUG: Resultado: {result}")
            return 'Error' not in str(result)
        except Exception as e:
            print(f"Erro ao mudar modo: {e}")
            import traceback
            traceback.print_exc()
            return False

    def set_color_hex(self, hex_color: str) -> bool:
        """
        Define a cor da lâmpada (modo colour)

        Args:
            hex_color: Cor em formato hexadecimal (ex: 'FF0000' para vermelho)
        """
        if not self.connected or not self.device:
            print("Dispositivo não conectado!")
            return False

        # Remove '#' se presente
        hex_color = hex_color.lstrip('#').upper()

        # Valida o formato
        if len(hex_color) != 6 or not all(c in '0123456789ABCDEFabcdef' for c in hex_color):
            print("Formato inválido! Use 6 caracteres hexadecimais (ex: FF0000)")
            return False

        # Converte hexadecimal para RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Usa o método set_colour do BulbDevice
        return self.set_color_rgb(r, g, b)

    def set_color_rgb(self, r: int, g: int, b: int) -> bool:
        """
        Define a cor da lâmpada usando valores RGB (0-255)

        Args:
            r: Valor de vermelho (0-255)
            g: Valor de verde (0-255)
            b: Valor de azul (0-255)
        """
        if not self.connected or not self.device:
            print("Dispositivo não conectado!")
            return False

        # Valida valores
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        print(f"DEBUG: Enviando cor RGB({r}, {g}, {b}) usando set_colour()")

        try:
            # Usa o método set_colour do BulbDevice que faz a conversão corretamente
            result = self.device.set_colour(r, g, b, nowait=False)
            print(f"DEBUG: Resultado: {result}")
            return 'Error' not in str(result)
        except Exception as e:
            print(f"Erro ao configurar cor: {e}")
            import traceback
            traceback.print_exc()
            return False

    def set_temperature(self, value: int) -> bool:
        """
        Define a temperatura da cor em modo white (porcentagem)

        Args:
            value: Valor de temperatura em porcentagem (0-100)
                   0% = branco frio (6500K)
                   100% = branco quente (2700K)
        """
        if not self.connected or not self.device:
            print("Dispositivo não conectado!")
            return False

        # Valida o intervalo (0-100%)
        value = max(0, min(100, value))

        print(f"DEBUG: Configurando temperatura para {value}%")

        try:
            # Usa set_colourtemp_percentage do BulbDevice
            result = self.device.set_colourtemp_percentage(value, nowait=False)
            print(f"DEBUG: Resultado: {result}")
            return 'Error' not in str(result)
        except Exception as e:
            print(f"Erro ao ajustar temperatura: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_info(self) -> str:
        """Retorna informações sobre a lâmpada"""
        info = f"""
┌─────────────────────────────────────┐
│     INFORMAÇÕES DA LÂMPADA          │
├─────────────────────────────────────┤
│ Nome: {self.config['name']}
│ ID: {self.config['id']}
│ IP: {self.config.get('ip', 'Não definido')}
│ Modelo: {self.config.get('model', 'N/A')}
│ Categoria: {self.config.get('category', 'N/A')}
│ Status: {'Conectada ✓' if self.connected else 'Desconectada ✗'}
│
│ Data Points:
│   - switch_led: DP {self.dp_switch}
│   - bright_value: DP {self.dp_brightness}
│   - work_mode: DP {self.dp_work_mode}
│   - colour_data: DP {self.dp_colour}
│   - temp_value: DP {self.dp_temperature}
└─────────────────────────────────────┘
"""
        return info

"""
END SmartLamp
"""

"""
===================
END Declaração de classes
===================
"""


"""
===================
BEGIN Declaração de funções
===================
"""

"""
BEGIN load_device_config
 - @param filename : Caminho do arquivo JSON com configurações dos dispositivos
 - @retparms devices : Lista de dicionários com configurações dos dispositivos
"""
def load_device_config(filename: str) -> list:
    """Carrega as configurações dos dispositivos de um arquivo JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        devices = json.load(f)
    return devices

"""
END load_device_config
"""

"""
BEGIN find_device_by_name
 - @param devices : Lista de dispositivos para procurar
 - @param name : Nome do dispositivo a ser encontrado
 - @retparms device : Dicionário com configuração do dispositivo encontrado ou None
"""
def find_device_by_name(devices: list, name: str) -> dict:
    """Encontra um dispositivo pelo nome"""
    for device in devices:
        if device['name'] == name:
            return device
    return None

"""
END find_device_by_name
"""

"""
BEGIN get_dp_from_mapping
 - @param device : Dicionário com configuração do dispositivo
 - @param code : Código da funcionalidade Tuya (ex: 'switch_led', 'bright_value')
 - @retparms dp : String com o Data Point correspondente ou None se não encontrado
"""
def get_dp_from_mapping(device: dict, code: str) -> str:
    """Extrai o DP (Data Point) baseado no código de funcionalidade"""
    mapping = device.get('mapping', {})
    for dp, info in mapping.items():
        if info.get('code') == code:
            return dp
    return None

"""
END get_dp_from_mapping
"""

"""
===================
END Declaração de funções
===================
"""