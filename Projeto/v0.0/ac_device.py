from greeclimate.device import Device as GreeDeviceClass
from lamp_device import IoTDevice

# Classe para dispositivo tipo ar condicionado (Gree)
class GreeDevice(IoTDevice):
    def __init__(self, name, ip, mac, status):
        super().__init__(name, "greeAC", status)
        self.ip = ip
        self.mac = mac
        self.device = GreeDeviceClass(ip, mac)
        try:
            self.device.connect()
        except Exception as e:
            print(f"  - ERRO ao conectar ao dispositivo Gree {name}: {e}")

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
