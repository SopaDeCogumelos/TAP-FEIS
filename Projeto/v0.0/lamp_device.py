import tinytuya as tuya

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
        try:
            # Força a leitura do status inicial para carregar as capacidades do dispositivo
            print(f"  - Obtendo status inicial de {name}...")
            status_data = self.device.status()
            if status_data and 'dps' in status_data and '20' in status_data['dps']:
                self.status = "on" if status_data['dps']['20'] else "off"
                print(f"  - Status de {name} atualizado para: {self.status}")
            else:
                print(f"  - Não foi possível determinar o status de {name} a partir da resposta: {status_data}")
        except Exception as e:
            print(f"  - ERRO ao obter status inicial de {name}: {e}")

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
