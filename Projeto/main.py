"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara
    Git: https://github.com/SopaDeCogumelos/TAP-FEIS

    Projeto Final - Gerenciamento de Dispositivos IoT

"""

# --- BEGIN Importações ---

# Importar suporte a arquivos json
import json

# Importar suporte a manipulação de arquivos e diretórios
import os

# Importar suporte a data e hora
from datetime import datetime

# Importar suporte a dispositivos IoT
import tinytuya as tuya
# from greeclimate.discovery import Discovery as GreeDiscovery
from lamp_device import TuyaDevice, bulb_control_menu
# from ac_device import GreeDevice, ac_control_menu

# --- END Importações ---

# --- BEGIN Declaração de Classes ---

# Classe para gerenciar leitura e salvamento de dados em arquivo JSON
class JsonManager:
    def __init__(self, filename):
        self.filename = filename

    # Função para ler dados de um arquivo JSON
    def read_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    # Função para escrever dados em um arquivo JSON, cria o arquivo se não existir
    def write_data(self, data):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

# Classe para gerenciar lista de dispositivos IoT
class IoTDeviceManager:
    def __init__(self, filename):
        self.json_manager = JsonManager(filename)
        self.data = self.json_manager.read_data()

    # Função para adicionar um novo dispositivo
    def add_device(self, device_name, device_info):
        self.data[device_name] = device_info
        self.json_manager.write_data(self.data)

    # Função para remover um dispositivo
    def remove_device(self, device_name):
        if device_name in self.data:
            del self.data[device_name]
            self.json_manager.write_data(self.data)

    # Função para listar todos os dispositivos
    def list_devices(self):
        return self.data

# --- END Declaração de Classes ---

# --- BEGIN Declaração de Funções ---

# Main function
def main():
    print("Programa Principal - Gerenciamento de Dispositivos IoT")
    device_manager = IoTDeviceManager("iot_devices.json")
    
    # Dicionário para manter os objetos de dispositivo "vivos"
    active_devices = {}

    # 1. Carregar e "hidratar" os dispositivos salvos no JSON
    print("\nCarregando dispositivos salvos...")
    saved_devices_data = device_manager.list_devices()
    for name, data in saved_devices_data.items():
        device_type = data.get("device_type")
        try:
            if device_type == "tuyaLamp":
                print(f"  - Recriando objeto Lâmpada: {name}")
                device = TuyaDevice(
                    name=name,
                    dev_id=data['dev_id'],
                    address=data['address'],
                    local_key=data['local_key'],
                    status=data.get('status', 'unknown')
                )
                active_devices[name] = device
            # elif device_type == "greeAC":
            #     print(f"  - Recriando objeto Ar Condicionado: {name}")
            #     device = GreeDevice(
            #         name=name,
            #         ip=data['ip'],
            #         mac=data['mac'],
            #         status=data.get('status', 'unknown')
            #     )
            #     active_devices[name] = device
        except KeyError as e:
            print(f"    ERRO: Faltando informação essencial ({e}) para o dispositivo {name}. Pulando.")
    
    # 2. Buscar novos dispositivos na rede (Tuya)
    print("\nBuscando dispositivos Tuya na rede local...")
    try:
        tuya_devices = tuya.deviceScan()
        print(f"Encontrados {len(tuya_devices)} dispositivos Tuya.")
        for dev_id, dev_info in tuya_devices.items():
            name = f"TuyaDevice_{dev_id[-6:]}"
            if name not in active_devices:
                print(f"  - Novo dispositivo Tuya encontrado: {name}")
                new_device = TuyaDevice(
                    name=name, 
                    dev_id=dev_id, 
                    address=dev_info['ip'], 
                    local_key=dev_info['key'], 
                    status="unknown"
                )
                device_manager.add_device(name, new_device.to_dict())
                active_devices[name] = new_device
                print(f"    Dispositivo '{name}' adicionado.")
    except Exception as e:
        print(f"ERRO ao escanear a rede por dispositivos Tuya: {e}")
    
    # # Adicionar aqui a busca por dispositivos Gree
    # print("\nBuscando dispositivos Gree na rede local...")
    # try:
    #     gree_devices_found = GreeDiscovery.discover()
    #     if gree_devices_found:
    #         print(f"Encontrados {len(gree_devices_found)} dispositivos Gree.")
    #         for dev_info in gree_devices_found:
    #             name = f"GreeDevice_{dev_info.mac.replace(':', '')[-6:]}
    #             if name not in active_devices:
    #                 print(f"  - Novo dispositivo Gree encontrado: {name} ({dev_info.ip})")
    #                 new_device = GreeDevice(
    #                     name=name,
    #                     ip=dev_info.ip,
    #                     mac=dev_info.mac,
    #                     status="unknown"
    #                 )
    #                 # A conexão é tentada no construtor. Adicionar apenas se a conexão for bem-sucedida.
    #                 if new_device.device.bound:
    #                     device_manager.add_device(name, new_device.to_dict())
    #                     active_devices[name] = new_device
    #                     print(f"    Dispositivo '{name}' adicionado.")
    #                 else:
    #                     print(f"    Falha ao conectar ao dispositivo Gree '{name}'. Não será adicionado.")
    # except Exception as e:
    #     print(f"ERRO ao escanear a rede por dispositivos Gree: {e}")


    # 3. Menu de Interação
    if not active_devices:
        print("\nNenhum dispositivo ativo encontrado. Encerrando.")
        return

    while True:
        print("\n--- Menu Principal ---")
        for i, (name, device) in enumerate(active_devices.items(), 1):
            print(f"{i}. {name} (Tipo: {device.device_type}, Status: {device.status})")
        print("0. Sair")

        choice = input("Escolha um dispositivo para interagir (ou 0 para sair): ")
        if choice == '0':
            break
        1
        try:
            dev_index = int(choice) - 1
            dev_name = list(active_devices.keys())[dev_index]
            selected_device = active_devices[dev_name]
            
            # Chama o menu apropriado com base no tipo de dispositivo
            if isinstance(selected_device, TuyaDevice):
                bulb_control_menu(selected_device)
            # elif isinstance(selected_device, GreeDevice):
            #     ac_control_menu(selected_device)
            else:
                print("Tipo de dispositivo desconhecido, sem menu de controle.")

        except (ValueError, IndexError):
            print("Opção inválida. Tente novamente.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

    print("\nPrograma encerrado.")
    return 

# --- END Declaração de Funções ---

# --- BEGIN Programa Principal ---
if __name__ == "__main__":
    main()
# --- END Programa Principal ---