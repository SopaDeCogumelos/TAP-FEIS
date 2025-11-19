"""
Módulo Wizard - Assistente de descoberta de dispositivos Tuya

Este módulo fornece uma interface programática para descobrir dispositivos
Tuya, conectando-se à nuvem para obter chaves locais e escaneando a rede
para obter endereços IP.
"""

import json
import time
import tinytuya

# ============================================================================
# BEGIN TuyaWizard
# ============================================================================
class TuyaWizard:
    """
    Classe para gerenciar o processo de descoberta de dispositivos Tuya.
    Substitui o wizard de linha de comando do tinytuya por uma implementação
    programática que pode ser integrada a interfaces gráficas.
    """

    # ============================================================================
    # BEGIN __init__
    # ============================================================================
    # @param api_key: str - Chave de API da Tuya (Access ID)
    # @param api_secret: str - Segredo da API da Tuya (Access Secret)
    # @param region: str - Região da conta (us, eu, cn, in)
    # @param device_id: str - ID de qualquer dispositivo da conta (para validação)
    # @retparms: None - Inicializa a instância
    def __init__(self, api_key: str, api_secret: str, region: str, device_id: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.region = region
        self.device_id = device_id
        self.cloud = None
        self.cloud_devices = []
        self.local_devices = {}
    # ============================================================================
    # END __init__
    # ============================================================================

    # ============================================================================
    # BEGIN connect
    # ============================================================================
    # @retparms: bool - True se a conexão for bem-sucedida, False caso contrário
    def connect(self) -> bool:
        """Conecta à nuvem Tuya usando as credenciais fornecidas"""
        try:
            self.cloud = tinytuya.Cloud(
                apiRegion=self.region,
                apiKey=self.api_key,
                apiSecret=self.api_secret,
                apiDeviceID=self.device_id
            )
            # Tenta uma operação simples para validar a conexão
            # Nota: tinytuya.Cloud não valida imediatamente, só no primeiro request
            return True
        except Exception as e:
            print(f"Erro ao conectar à nuvem Tuya: {e}")
            return False
    # ============================================================================
    # END connect
    # ============================================================================

    # ============================================================================
    # BEGIN fetch_devices
    # ============================================================================
    # @retparms: list - Lista de dispositivos encontrados na nuvem
    def fetch_devices(self) -> list:
        """Busca a lista de dispositivos registrados na conta Tuya"""
        if not self.cloud:
            if not self.connect():
                return []

        try:
            # Obtém dispositivos da nuvem
            # Nota: Algumas versões do tinytuya podem retornar dict mesmo com verbose=False
            result = self.cloud.getdevices(verbose=False)
            
            if isinstance(result, dict):
                if 'result' in result:
                    self.cloud_devices = result['result']
                elif 'devices' in result:
                    self.cloud_devices = result['devices']
                else:
                    # Tenta usar o próprio dict se parecer ser um mapa de dispositivos
                    # Mas geralmente 'result' contém a lista
                    print(f"Aviso: Formato de retorno inesperado da nuvem: {type(result)}")
                    print(f"Conteúdo do retorno: {result}")
                    self.cloud_devices = []
            elif isinstance(result, list):
                self.cloud_devices = result
            else:
                self.cloud_devices = []

            return self.cloud_devices
        except Exception as e:
            print(f"Erro ao buscar dispositivos na nuvem: {e}")
            return []
    # ============================================================================
    # END fetch_devices
    # ============================================================================

    # ============================================================================
    # BEGIN scan_local
    # ============================================================================
    # @param timeout: int - Tempo máximo de busca em segundos (padrão: 8)
    # @retparms: dict - Dicionário de dispositivos encontrados na rede local
    def scan_local(self, timeout: int = 8) -> dict:
        """Escaneia a rede local em busca de dispositivos Tuya ativos"""
        try:
            # tinytuya.deviceScan não aceita 'scantime' em algumas versões
            # Usamos forcescan=True para forçar o envio de pacotes de descoberta
            print(f"   (Debug: Iniciando scan com forcescan=True)")
            devices = tinytuya.deviceScan(forcescan=True)
            
            # Converte para dicionário indexado por ID para fácil acesso
            self.local_devices = {}
            for d in devices:
                if 'id' in d: # Protocolo 3.3+
                    self.local_devices[d['id']] = d
                elif 'gwId' in d: # Protocolo 3.1
                    self.local_devices[d['gwId']] = d
            
            return self.local_devices
        except Exception as e:
            print(f"Erro ao escanear rede local: {e}")
            return {}
    # ============================================================================
    # END scan_local
    # ============================================================================

    # ============================================================================
    # BEGIN merge_data
    # ============================================================================
    # @retparms: list - Lista combinada de dispositivos com chaves e IPs
    def merge_data(self) -> list:
        """Combina dados da nuvem (chaves) com dados locais (IPs)"""
        merged_list = []

        if not self.cloud_devices:
            return []

        for c_dev in self.cloud_devices:
            # Garante que c_dev é um dicionário
            if not isinstance(c_dev, dict):
                continue

            dev_id = c_dev.get('id')
            name = c_dev.get('name')
            key = c_dev.get('key')
            mac = c_dev.get('mac')
            
            # Cria objeto base
            device_entry = {
                "name": name,
                "id": dev_id,
                "key": key,
                "mac": mac,
                "ip": "",
                "version": "3.3", # Padrão assumido
                "product_key": c_dev.get('product_key', '')
            }

            # Tenta encontrar IP na lista local
            if dev_id in self.local_devices:
                l_dev = self.local_devices[dev_id]
                device_entry['ip'] = l_dev.get('ip')
                device_entry['version'] = l_dev.get('version', '3.3')
            
            merged_list.append(device_entry)

        return merged_list
    # ============================================================================
    # END merge_data
    # ============================================================================

# ============================================================================
# END TuyaWizard
# ============================================================================
