"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara
    Git: https://github.com/SopaDeCogumelos/TAP-FEIS

    Projeto Final - Gerenciamento de Dispositivos IoT - v0.1

"""

# --- BEGIN Importações ---
import json
import os
from pathlib import Path
from tuya_device import TuyaDevice
# --- END Importações ---

# --- BEGIN Declaração de Classes ---

# Classe para gerenciar leitura e salvamento de dados em arquivo JSON
class JsonManager:
    """
    Classe para gerenciar a leitura e escrita de dados em um arquivo JSON.
    """
    def __init__(self, filename):
        """
        Inicializa o JsonManager com o nome do arquivo.
        """
        self.filename = filename

    def read_data(self):
        """
        Lê os dados do arquivo JSON.
        Retorna um dicionário com os dados ou um dicionário vazio se o arquivo não existir ou estiver mal formatado.
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            # Retorna um dicionário vazio se o arquivo estiver vazio ou mal formatado
            return {}
    
    def write_data(self, data):
        """
        Escreve os dados em um arquivo JSON.
        Cria o arquivo se ele não existir.
        """
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

class DeviceManager:
    """
    Gerencia o ciclo de vida dos dispositivos IoT: carregar, salvar, adicionar e remover.
    """
    def __init__(self, filename="iot_devices.json", tuya_devices_file="../tuya_devices.json"):
        self.json_manager = JsonManager(filename)
        self.tuya_devices_file = tuya_devices_file
        self.devices = {}
        self.load_devices()
        self.import_from_tuya_api()

    def load_devices(self):
        """
        Carrega os dispositivos do arquivo JSON e cria as instâncias de objeto.
        """
        print("\nCarregando dispositivos salvos...")
        saved_data = self.json_manager.read_data()
        for name, data in saved_data.items():
            device_type = data.get("device_type")
            try:
                if device_type == "tuya_lamp":
                    print(f"  - Criando objeto para: {name}")
                    device = TuyaDevice(
                        name=name,
                        dev_id=data['dev_id'],
                        address=data['address'],
                        local_key=data['local_key'],
                        status=data.get('status', 'unknown')
                    )
                    self.devices[name] = device
            except KeyError as e:
                print(f"    ERRO: Faltando informação essencial ({e}) para o dispositivo {name}. Pulando.")
        print("Dispositivos carregados.")

    def save_devices(self):
        """
        Converte todos os objetos de dispositivo em dicionários e salva no arquivo JSON.
        """
        data_to_save = {name: device.to_dict() for name, device in self.devices.items()}
        self.json_manager.write_data(data_to_save)
        print("Dispositivos salvos com sucesso.")

    def import_from_tuya_api(self):
        """
        Importa dispositivos a partir do arquivo de configuração da API Tuya.
        Se o arquivo não existir ou estiver vazio, esta função é silenciosamente ignorada.
        """
        import os
        
        if not os.path.exists(self.tuya_devices_file):
            return  # Arquivo não existe, continua normalmente
        
        try:
            with open(self.tuya_devices_file, 'r', encoding='utf-8') as f:
                tuya_data = json.load(f)
            
            if not isinstance(tuya_data, list):
                return  # Formato não esperado
            
            print("\nImportando dispositivos da API Tuya...")
            imported_count = 0
            
            for device_info in tuya_data:
                try:
                    name = device_info.get('name', f"Device_{device_info.get('id', 'unknown')[:6]}")
                    dev_id = device_info.get('id')
                    local_key = device_info.get('key')
                    mac = device_info.get('mac')
                    
                    # Verifica se temos os dados necessários
                    if not dev_id or not local_key:
                        continue
                    
                    # Se o dispositivo já existe, pula
                    if name in self.devices:
                        continue
                    
                    # Tenta criar o dispositivo
                    # Para dispositivos Tuya, usamos um IP placeholder ou tentamos descobrir
                    # Por enquanto, usamos o MAC ou um valor padrão
                    address = device_info.get('ip', '0.0.0.0')  # O IP será descoberto pela chave local
                    
                    device = TuyaDevice(
                        name=name,
                        dev_id=dev_id,
                        address=address,
                        local_key=local_key
                    )
                    self.devices[name] = device
                    imported_count += 1
                    print(f"  - Dispositivo importado: {name}")
                    
                except Exception as e:
                    print(f"  - Erro ao importar dispositivo: {e}")
            
            if imported_count > 0:
                self.save_devices()
                print(f"Total de {imported_count} dispositivo(s) importado(s) da API Tuya.")
        
        except json.JSONDecodeError:
            print(f"AVISO: O arquivo '{self.tuya_devices_file}' não está em formato JSON válido.")
        except Exception as e:
            print(f"AVISO: Erro ao importar dispositivos da API Tuya: {e}")

    def add_device_interactive(self):
        """
        Guia o usuário para adicionar um novo dispositivo Tuya.
        Tenta importar a local_key automaticamente de várias fontes.
        """
        found_devices = TuyaDevice.scan_devices()
        if not found_devices:
            print("Nenhum novo dispositivo Tuya encontrado na rede.")
            return

        print("\nDispositivos Tuya encontrados na rede:")
        for i, (dev_id, info) in enumerate(found_devices.items(), 1):
            print(f"{i}. ID: {dev_id}, IP: {info['ip']}")

        try:
            choice = int(input("Escolha o número do dispositivo para adicionar (ou 0 para cancelar): "))
            if choice == 0:
                return

            dev_id = list(found_devices.keys())[choice - 1]
            dev_info = found_devices[dev_id]
            
            name = input(f"Digite um nome para o dispositivo '{dev_id[-6:]}': ")
            if not name:
                name = f"TuyaDevice_{dev_id[-6:]}"
            name = name.strip()

            if name in self.devices:
                print(f"ERRO: Um dispositivo com o nome '{name}' já existe.")
                return

            # Tenta obter a local_key automaticamente
            local_key = self._get_local_key_automatically(dev_id, dev_info)
            
            if not local_key:
                # Se não conseguir, solicita ao usuário
                print("\nAVISO: A 'local_key' é necessária para controlar o dispositivo.")
                print("Você pode obtê-la usando ferramentas como 'tuya-cli wizard' ou verificar no arquivo tuya_devices.json.")
                local_key = input(f"Digite a 'local_key' para o dispositivo '{name}': ").strip()

                if not local_key:
                    print("ERRO: A 'local_key' não pode ser vazia. Adição cancelada.")
                    return
            else:
                print(f"\n✓ Local_key obtida automaticamente!")

            new_device = TuyaDevice(
                name=name,
                dev_id=dev_id,
                address=dev_info['ip'],
                local_key=local_key
            )
            self.devices[name] = new_device
            self.save_devices()
            print(f"Dispositivo '{name}' adicionado com sucesso.")

        except (ValueError, IndexError):
            print("Opção inválida.")

    def _get_local_key_automatically(self, dev_id, dev_info):
        """
        Tenta obter a local_key de várias fontes:
        1. Do arquivo tuya_devices.json (se estiver no diretório raiz)
        2. Do arquivo de configuração do tinytuya (~/.tinytuya/devices.json)
        3. Da busca de rede (se retornar a chave)
        """
        # 1. Tenta do arquivo tuya_devices.json no diretório raiz
        tuya_api_file = Path("../tuya_devices.json")
        if tuya_api_file.exists():
            try:
                with open(tuya_api_file, 'r', encoding='utf-8') as f:
                    tuya_data = json.load(f)
                if isinstance(tuya_data, list):
                    for device in tuya_data:
                        if device.get('id') == dev_id and device.get('key'):
                            print(f"  - Local_key encontrada em tuya_devices.json")
                            return device['key']
            except Exception:
                pass
        
        # 2. Tenta do arquivo de configuração do tinytuya
        tinytuya_config_paths = [
            Path.home() / ".tinytuya" / "devices.json",
            Path.home() / ".local" / "share" / "tinytuya" / "devices.json",
            Path.home() / "AppData" / "Local" / "tinytuya" / "devices.json",  # Windows
        ]
        
        for config_path in tinytuya_config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # Pode estar em diferentes formatos
                    if isinstance(config_data, dict):
                        # Formato: {device_id: {info}}
                        if dev_id in config_data and 'key' in config_data[dev_id]:
                            print(f"  - Local_key encontrada em configuração do tinytuya")
                            return config_data[dev_id]['key']
                    elif isinstance(config_data, list):
                        # Formato: [{id, key, ...}]
                        for device in config_data:
                            if device.get('id') == dev_id and device.get('key'):
                                print(f"  - Local_key encontrada em configuração do tinytuya")
                                return device['key']
                except Exception:
                    pass
        
        # 3. Tenta do retorno da busca de rede (raramente retorna)
        if 'key' in dev_info and dev_info['key']:
            print(f"  - Local_key obtida da busca de rede")
            return dev_info['key']
        
        return None

    def remove_device_interactive(self):
        """
        Guia o usuário para remover um dispositivo existente.
        """
        if not self.devices:
            print("Nenhum dispositivo salvo para remover.")
            return

        print("\nSelecione o dispositivo para remover:")
        device_list = list(self.devices.keys())
        for i, name in enumerate(device_list, 1):
            print(f"{i}. {name}")

        try:
            choice = int(input("Escolha o número do dispositivo (ou 0 para cancelar): "))
            if choice == 0:
                return
            
            name_to_remove = device_list[choice - 1]
            del self.devices[name_to_remove]
            self.save_devices()
            print(f"Dispositivo '{name_to_remove}' removido com sucesso.")

        except (ValueError, IndexError):
            print("Opção inválida.")

# --- END Declaração de Classes ---

# --- BEGIN Declaração de Funções ---

def device_control_menu(device: TuyaDevice):
    """
    Exibe um menu de controle para um dispositivo Tuya específico.
    """
    while True:
        print(f"\n--- Controle de '{device.name}' (Status: {device.status}) ---")
        print("1. Ligar")
        print("2. Desligar")
        print("3. Alternar (Toggle)")
        print("4. Mudar Brilho (%)")
        print("5. Mudar Temperatura da Cor (%)")
        print("6. Mudar Cor (RGB)")
        print("0. Voltar ao Menu Principal")
        
        choice = input("Escolha uma ação: ")
        success, message = False, ""

        try:
            if choice == '1':
                success, message = device.turn_on()
            elif choice == '2':
                success, message = device.turn_off()
            elif choice == '3':
                success, message = device.toggle()
            elif choice == '4':
                brightness = int(input("  - Digite o brilho (0-100): "))
                success, message = device.set_brightness(brightness)
            elif choice == '5':
                temp = int(input("  - Digite a temperatura (0-100): "))
                success, message = device.set_color_temp(temp)
            elif choice == '6':
                r = int(input("  - Valor de Vermelho (0-255): "))
                g = int(input("  - Valor de Verde (0-255): "))
                b = int(input("  - Valor de Azul (0-255): "))
                success, message = device.set_color(r, g, b)
            elif choice == '0':
                break
            else:
                print("Opção inválida.")
            
            if message:
                print(f"  -> {message}")

        except ValueError:
            print("  ERRO: Entrada inválida. Por favor, insira um número.")
        except Exception as e:
            print(f"  ERRO inesperado: {e}")

def main():
    """
    Função principal que executa o programa de gerenciamento de dispositivos.
    """
    device_manager = DeviceManager("iot_devices.json")

    while True:
        print("\n--- Menu Principal ---")
        print("Dispositivos Salvos:")
        if not device_manager.devices:
            print("  Nenhum dispositivo cadastrado.")
        else:
            for name, device in device_manager.devices.items():
                # O status 'unknown' indica que a inicialização falhou (offline)
                online_status = "Online" if device.status != "unknown" else "Offline"
                print(f"  - {name} (Tipo: {device.device_type}, Status: {device.status}, Rede: {online_status})")
        
        print("\n============================")
        print("1. Selecionar um dispositivo")
        print("2. Adicionar Novo Dispositivo (Tuya)")
        print("3. Remover Dispositivo")
        print("0. Sair")
        print("============================")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            if not device_manager.devices:
                print("Nenhum dispositivo para selecionar.")
                continue
            
            print("\nSelecione o dispositivo para controlar:")
            device_list = list(device_manager.devices.keys())
            for i, name in enumerate(device_list, 1):
                print(f"{i}. {name}")
            
            try:
                dev_choice = int(input("Escolha o número do dispositivo: "))
                selected_name = device_list[dev_choice - 1]
                selected_device = device_manager.devices[selected_name]
                
                if selected_device.status == "unknown":
                    print(f"AVISO: O dispositivo '{selected_name}' parece estar offline. Os comandos podem falhar.")

                # Chama o menu de controle específico
                if isinstance(selected_device, TuyaDevice):
                    device_control_menu(selected_device)
                else:
                    print("Tipo de dispositivo não suportado para controle.")

            except (ValueError, IndexError):
                print("Opção inválida.")

        elif choice == '2':
            device_manager.add_device_interactive()
        elif choice == '3':
            device_manager.remove_device_interactive()
        elif choice == '0':
            print("Salvando alterações e encerrando...")
            device_manager.save_devices()
            break
        else:
            print("Opção inválida. Tente novamente.")

# --- END Declaração de Funções ---

# --- BEGIN Programa Principal ---
if __name__ == "__main__":
    main()
# --- END Programa Principal ---