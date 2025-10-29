"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara
    Git: https://github.com/SopaDeCogumelos/TAP-FEIS

"""

# --- BEGIN Importações ---

# Importar suporte a arquivos json
import json

# Importar suporte a manipulação de arquivos e diretórios
import os

# Importar suporte a data e hora
from datetime import datetime

# Importar suporte a dispositivos IoT
import tinytuya as tuya # Biblioteca para controlar dispositivos Tuya
import greeclimate as gree # Biblioteca para controlar dispositivos Gree

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

# Classe para representar um dispositivo IoT
class IoTDevice:
    def __init__(self, name, device_type, status):
        self.name = name
        self.device_type = device_type
        self.status = status

    def to_dict(self):
        return {
            "name": self.name,
            "device_type": self.device_type,
            "status": self.status
        }

# Classe para dispositivo tipo lampada (Tuya)
#   Devera incluir leitura dos dispositivos salvos no arquivo JSON e escrita de novos dispositivos (BulbDevice)
class TuyaDevice(IoTDevice):
    def __init__(self, name, dev_id, address, local_key, status):
        super().__init__(name, "tuyaLamp", status)
        self.dev_id = dev_id
        self.address = address
        self.local_key = local_key
        self.device = tuya.BulbDevice(dev_id, address, local_key)
        self.device.set_version(3.3)

    def turn_on(self):
        try:
            self.device.turn_on()
            self.status = "on"
            return True, "Dispositivo ligado com sucesso."
        except Exception as e:
            return False, f"ERRO: {str(e)}"

    def turn_off(self):
        try:
            self.device.turn_off()
            self.status = "off"
            return True, "Dispositivo desligado com sucesso."
        except Exception as e:
            return False, f"ERRO: {str(e)}"

    def toggle(self):
        try:
            self.device.toggle()
            self.status = "on" if self.status == "off" else "off"
            return True, "Comando toggle enviado com sucesso."
        except Exception as e:
            return False, f"ERRO: {str(e)}"
    
    # Função para encapsular os dados do dispositivo em um dicionário
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "dev_id": self.dev_id,
            "address": self.address,
            "local_key": self.local_key
        })
        return base_dict

    # Função para ler ao estado atual do dispositivo
    def read_status(self):
        status = self.device.status()
        return status
    
    # Função para ler a configuração atual do dispositivo
    def read_configuration(self):
        config = self.device.detect_available_dps()
        return config
    
    # função que retorna a configuração do bulbdevice (modo, cor, brilho, temperatura de cor)
    def get_bulb_configuration(self):
        status = self.read_status()
        config = {
            "mode": status.get('dps', {}).get('20', 'unknown'),
            "color": status.get('dps', {}).get('16', 'unknown'),
            "brightness": status.get('dps', {}).get('22', 'unknown'),
            "color_temp": status.get('dps', {}).get('23', 'unknown')
        }
        return config
    
    # Função para mudar o configuração do bulbdevice (modo: white (brightness, temp), colour (r, g, b), music)
    def set_bulb_configuration(self, mode, **kwargs):
        try:
            if mode == "white":
                brightness = kwargs.get('brightness', 100)
                color_temp = kwargs.get('color_temp', 0)
                self.device.set_white_percentage(brightness, color_temp)
            elif mode == "colour":
                r = kwargs.get('r', 255)
                g = kwargs.get('g', 255)
                b = kwargs.get('b', 255)
                self.device.set_colour(r, g, b)
            elif mode == "music":
                self.device.set_music()
            self.status = mode
            return True, "Configuração alterada com sucesso."
        except Exception as e:
            return False, f"ERRO: {str(e)}"      

# Classe para dispositivo tipo ar condicionado (Gree)
class GreeDevice(IoTDevice):
    def __init__(self, name, ip, mac, status):
        super().__init__(name, "greeAC", status)
        self.ip = ip
        self.mac = mac
        self.device = gree.GreeClimate(ip, mac)

    # Função para encapsular os dados do dispositivo em um dicionário
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "ip": self.ip,
            "mac": self.mac
        })
        return base_dict

    def turn_on(self):
        try:
            self.device.set_power(True)
            self.status = "on"
            return True, "Ar condicionado ligado com sucesso."
        except Exception as e:
            return False, f"ERRO: {str(e)}"

    def turn_off(self):
        try:
            self.device.set_power(False)
            self.status = "off"
            return True, "Ar condicionado desligado com sucesso."
        except Exception as e:
            return False, f"ERRO: {str(e)}"

    # Função para ajustar a temperatura do ar condicionado
    def set_temperature(self, temperature):
        try:
            self.device.set_target_temperature(temperature)
            return True, f"Temperatura ajustada para {temperature}°C com sucesso."
        except Exception as e:
            return False, f"ERRO: {str(e)}"
        
    # Função para ajustar velocidade do ventilador
    def set_fan_speed(self, fan_speed):
        try:
            # Fan speed values are usually 0-5 for Gree devices
            self.device.set_fan_speed(fan_speed)
            return True, f"Velocidade do ventilador ajustada para {fan_speed}."
        except Exception as e:
            return False, f"ERRO: {str(e)}"
        
    # Função para ler os atributos atuais do ar condicionado
    def get_status(self):
        try:
            # The greeclimate library updates the object's state on method calls
            # We can build a status dictionary from its properties
            return {
                "power": self.device.power,
                "mode": self.device.mode,
                "target_temperature": self.device.target_temperature,
                "current_temperature": self.device.current_temperature,
                "fan_speed": self.device.fan_speed
            }
        except Exception as e:
            return {"error": str(e)}

# --- END Declaração de Classes ---

# --- BEGIN Declaração de Funções ---

# Função do menu de controle de lampadas IoT
def bulb_control_menu(device: TuyaDevice):
    print("\n--- Menu de Controle de Lâmpadas ---")
    while True:
        print("1. Mudar para modo White")
        print("2. Mudar para modo Colour")
        print("3. Mudar para modo Music")
        print("0. Voltar")

        choice = input("Escolha uma ação: ")

        if choice == '0':
            break
        
        try:
            if choice == '1':
                brightness = int(input("  - Defina o brilho (0-100): "))
                color_temp = int(input("  - Defina a temperatura de cor (0-100): "))
                success, message = device.set_bulb_configuration("white", brightness=brightness, color_temp=color_temp)
                print(f"  - {message}")
            elif choice == '2':
                r = int(input("  - Defina o valor R (0-255): "))
                g = int(input("  - Defina o valor G (0-255): "))
                b = int(input("  - Defina o valor B (0-255): "))
                success, message = device.set_bulb_configuration("colour", r=r, g=g, b=b)
                print(f"  - {message}")
            elif choice == '3':
                success, message = device.set_bulb_configuration("music")
                print(f"  - {message}")
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("  - ERRO: Por favor, insira apenas números.")
        except Exception as e:
            print(f"  - ERRO inesperado: {e}")

# Função do menu de controle de ar condicionado IoT
def ac_control_menu(device: GreeDevice):
    print("\n--- Menu de Controle de Ar Condicionado ---")
    while True:
        print("1. Ligar")
        print("2. Desligar")
        print("3. Ajustar Temperatura")
        print("4. Ajustar Velocidade do Ventilador (0-5)")
        print("0. Voltar")

        choice = input("Escolha uma ação: ")

        if choice == '0':
            break
        
        try:
            if choice == '1':
                success, message = device.turn_on()
                print(f"  - {message}")
            elif choice == '2':
                success, message = device.turn_off()
                print(f"  - {message}")
            elif choice == '3':
                temp = int(input("  - Defina a temperatura (ex: 22): "))
                success, message = device.set_temperature(temp)
                print(f"  - {message}")
            elif choice == '4':
                speed = int(input("  - Defina a velocidade do ventilador (0-5): "))
                if 0 <= speed <= 5:
                    success, message = device.set_fan_speed(speed)
                    print(f"  - {message}")
                else:
                    print("  - Velocidade inválida. Deve ser entre 0 e 5.")
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("  - ERRO: Por favor, insira apenas números.")
        except Exception as e:
            print(f"  - ERRO inesperado: {e}")


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
            elif device_type == "greeAC":
                print(f"  - Recriando objeto Ar Condicionado: {name}")
                device = GreeDevice(
                    name=name,
                    ip=data['ip'],
                    mac=data['mac'],
                    status=data.get('status', 'unknown')
                )
                active_devices[name] = device
        except KeyError as e:
            print(f"    ERRO: Faltando informação essencial ({e}) para o dispositivo {name}. Pulando.")
    
    # 2. Buscar novos dispositivos na rede (Tuya)
    print("\nBuscando dispositivos Tuya na rede local...")
    try:
        tuya_devices = tuya.deviceScan(max_time=10)
        print(f"Encontrados {len(tuya_devices)} dispositivos Tuya.")
        for dev_id, dev_info in tuya_devices.items():
            name = f"TuyaDevice_{dev_id[-4:]}"
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
    
    # Adicionar aqui a busca por dispositivos Gree, se a biblioteca suportar
    # A biblioteca greeclimate não possui uma função de scan, então eles devem ser adicionados manualmente no JSON.


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
        
        try:
            dev_index = int(choice) - 1
            dev_name = list(active_devices.keys())[dev_index]
            selected_device = active_devices[dev_name]
            
            # Chama o menu apropriado com base no tipo de dispositivo
            if isinstance(selected_device, TuyaDevice):
                bulb_control_menu(selected_device)
            elif isinstance(selected_device, GreeDevice):
                ac_control_menu(selected_device)
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