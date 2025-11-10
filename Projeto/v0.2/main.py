"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara
    Git: https://github.com/SopaDeCogumelos/TAP-FEIS

    Projeto Final - Gerenciamento de Dispositivos IoT - v0.2
    
    Controle de lâmpada Tuya com interface interativa

"""

import json
import time
import tinytuya
import os


def load_device_config(filename: str) -> list:
    """Carrega as configurações dos dispositivos de um arquivo JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        devices = json.load(f)
    return devices


def find_device_by_name(devices: list, name: str) -> dict:
    """Encontra um dispositivo pelo nome"""
    for device in devices:
        if device['name'] == name:
            return device
    return None


def get_dp_from_mapping(device: dict, code: str) -> str:
    """Extrai o DP (Data Point) baseado no código de funcionalidade"""
    mapping = device.get('mapping', {})
    for dp, info in mapping.items():
        if info.get('code') == code:
            return dp
    return None


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
        
        # Extrai DPs importantes
        self.dp_switch = get_dp_from_mapping(device_config, 'switch_led')
        self.dp_brightness = get_dp_from_mapping(device_config, 'bright_value')
        self.dp_work_mode = get_dp_from_mapping(device_config, 'work_mode')
        self.dp_colour = get_dp_from_mapping(device_config, 'colour_data')
        self.dp_temperature = get_dp_from_mapping(device_config, 'temp_value')
        
    def connect(self) -> bool:
        """Conecta ao dispositivo"""
        try:
            # Usa BulbDevice ao invés de OutletDevice para ter acesso aos métodos de cor
            self.device = tinytuya.BulbDevice(
                dev_id=self.config['id'],
                address=self.config.get('ip', 'scan'),
                local_key=self.config['key'],
                version=self.version
            )
            
            if self.config.get('ip'):
                self.device.address = self.config['ip']
            
            # Tenta obter status para verificar conexão
            status = self.device.status()
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Erro ao conectar: {e}")
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


def clear_screen():
    """Limpa a tela do console"""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_status_readable(lamp: SmartLamp) -> str:
    """Formata o status da lâmpada de forma legível"""
    status = lamp.get_status()
    
    if not status:
        return "❌ Erro ao obter status da lâmpada"
    
    if 'Error' in str(status):
        return f"❌ Erro: {status}"
    
    # Extrai informações do status
    state_data = {}
    if 'dps' in status:
        for dp, value in status['dps'].items():
            state_data[dp] = value
    
    # Mapeia os DPs para informações legíveis
    is_on = state_data.get(lamp.dp_switch, False)
    brightness = state_data.get(lamp.dp_brightness, 0)
    mode = state_data.get(lamp.dp_work_mode, 'Desconhecido')
    temperature = state_data.get(lamp.dp_temperature, 0)
    colour_data = state_data.get(lamp.dp_colour, '')
    
    # Converte para porcentagem se necessário
    if brightness and lamp.device and hasattr(lamp.device, 'dpset'):
        if lamp.device.dpset.get('value_max'):
            brightness_pct = int((brightness / lamp.device.dpset['value_max']) * 100)
        else:
            brightness_pct = brightness
    else:
        brightness_pct = brightness
    
    if temperature and lamp.device and hasattr(lamp.device, 'dpset'):
        if lamp.device.dpset.get('value_max'):
            temperature_pct = int((temperature / lamp.device.dpset['value_max']) * 100)
        else:
            temperature_pct = temperature
    else:
        temperature_pct = temperature
    
    # Extrai cor em formato legível (se disponível)
    color_display = "N/A"
    if colour_data:
        try:
            # colour_data geralmente vem como string "rrggbbhhhssvv"
            if isinstance(colour_data, str) and len(colour_data) >= 6:
                hex_color = colour_data[:6].upper()
                color_display = f"#{hex_color}"
        except:
            color_display = str(colour_data)[:20]  # Limita a 20 caracteres
    
    # Monta o status formatado
    status_text = f"""
┌─────────────────────────────────────┐
│          STATUS DA LÂMPADA          │
├─────────────────────────────────────┤
│ Ligada: {'✓ Sim' if is_on else '✗ Não'}
│ Modo: {mode}
│ Brilho: {brightness_pct}%
│ Temperatura: {temperature_pct}%
│ Cor: {color_display}
└─────────────────────────────────────┘
"""
    return status_text


def print_menu():
    """Exibe o menu principal"""
    print("""
╔═════════════════════════════════════════╗
║     CONTROLE DE LÂMPADA INTELIGENTE     ║
╠═════════════════════════════════════════╣
║  1. Liga/Desliga                        ║
║  2. Ajustar brilho                      ║
║  3. Ajustar temperatura                 ║
║  4. Configurar cor                      ║
║  5. Ver status                          ║
║  6. Debug                               ║
║  0. Sair                                ║
╚═════════════════════════════════════════╝
""")


# ============================================================================
# FUNÇÕES DOS SUBMENUS
# ============================================================================

def toggle_power(lamp: SmartLamp):
    """Opção 1: Liga ou desliga a lâmpada"""
    status = lamp.get_status()
    is_on = False
    
    if status and 'dps' in status:
        is_on = status['dps'].get(lamp.dp_switch, False)
    
    if is_on:
        print("\n🌙 Desligando lâmpada...")
        if lamp.turn_off():
            print("✓ Lâmpada desligada com sucesso!")
        else:
            print("✗ Erro ao desligar lâmpada")
    else:
        print("\n🔆 Ligando lâmpada...")
        if lamp.turn_on():
            print("✓ Lâmpada ligada com sucesso!")
        else:
            print("✗ Erro ao ligar lâmpada")

    print(lamp.get_info())


def show_status(lamp: SmartLamp):
    """Opção 5: Exibe o status formatado"""
    print(format_status_readable(lamp))


def set_brightness(lamp: SmartLamp):
    """Opção 2: Ajusta o brilho"""
    try:
        brightness = int(input("\n💡 Digite o valor de brilho (0-100%): "))
        print(f"Ajustando brilho para {brightness}%...")
        if lamp.set_brightness(brightness):
            print("✓ Brilho ajustado com sucesso!")
        else:
            print("✗ Erro ao ajustar brilho")
    except ValueError:
        print("✗ Valor inválido!")


def set_temperature(lamp: SmartLamp):
    """Opção 3: Ajusta a temperatura"""
    print("\n🌡️ Ajustar Temperatura da Luz")
    print("━" * 40)
    print("Escala de temperatura (0-100%):")
    print("  0%   = Branco Frio (6500K)")
    print("  50%  = Branco Neutro (4000K)")
    print("  100% = Branco Quente (2700K)")
    
    try:
        temp = int(input("\nDigite o valor de temperatura (0-100%): "))
        print(f"Ajustando temperatura para {temp}%...")
        if lamp.set_temperature(temp):
            print("✓ Temperatura ajustada com sucesso!")
        else:
            print("✗ Erro ao ajustar temperatura")
    except ValueError:
        print("✗ Valor inválido!")


def set_color(lamp: SmartLamp):
    """Opção 4: Configura a cor da lâmpada"""
    print("\n� Configurar Cor da Lâmpada")
    print("━" * 40)
    print("Escolha como inserir a cor:")
    print("  1. Por código hexadecimal (ex: FF0000)")
    print("  2. Por valores RGB (ex: 255, 0, 0)")
    print("  3. Cores pré-definidas")
    
    color_choice = input("Escolha: ").strip()
    
    if color_choice == '1':
        set_color_by_hex(lamp)
    elif color_choice == '2':
        set_color_by_rgb(lamp)
    elif color_choice == '3':
        set_color_by_preset(lamp)
    else:
        print("✗ Opção inválida!")


def print_debug_menu():
    """Exibe o submenu de debug"""
    print("""
╔═════════════════════════════════════════╗
║            MENU DEBUG                   ║
╠═════════════════════════════════════════╣
║  1. Informações da lâmpada              ║
║  2. Sequência de comandos               ║
║  0. Voltar                              ║
╚═════════════════════════════════════════╝
""")


def show_debug_menu(lamp: SmartLamp):
    """Opção 6: Menu de debug"""
    while True:
        print_debug_menu()
        choice = input("Escolha uma opção: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            print(lamp.get_info())
        elif choice == '2':
            print("\n🔄 Executando sequência de testes...")
            test_sequence(lamp)
        else:
            print("✗ Opção inválida!")
        
        if choice != '0':
            input("\nPressione ENTER para continuar...")
            clear_screen()


def set_color_by_hex(lamp: SmartLamp):
    """Submenu: Define cor por hexadecimal"""
    hex_input = input("Digite a cor em hexadecimal (ex: FF0000): ").strip()
    if lamp.set_color_hex(hex_input):
        print("✓ Cor definida com sucesso!")
    else:
        print("✗ Erro ao definir cor")


def set_color_by_rgb(lamp: SmartLamp):
    """Submenu: Define cor por RGB"""
    try:
        r = int(input("Digite valor de VERMELHO (0-255): "))
        g = int(input("Digite valor de VERDE (0-255): "))
        b = int(input("Digite valor de AZUL (0-255): "))
        
        if lamp.set_color_rgb(r, g, b):
            print("✓ Cor definida com sucesso!")
        else:
            print("✗ Erro ao definir cor")
    except ValueError:
        print("✗ Valores inválidos!")


def set_color_by_preset(lamp: SmartLamp):
    """Submenu: Define cor por pré-definidas"""
    colors = {
        '1': ('FF0000', 'Vermelho'),
        '2': ('00FF00', 'Verde'),
        '3': ('0000FF', 'Azul'),
        '4': ('FFFF00', 'Amarelo'),
        '5': ('FF00FF', 'Magenta'),
        '6': ('00FFFF', 'Ciano'),
        '7': ('FFFFFF', 'Branco'),
        '8': ('FF7F00', 'Laranja'),
        '9': ('800080', 'Roxo'),
    }
    
    print("\nCores disponíveis:")
    for key, (_, name) in colors.items():
        print(f"  {key}. {name}")
    
    color_input = input("Escolha: ").strip()
    if color_input in colors:
        hex_code, color_name = colors[color_input]
        print(f"Definindo cor: {color_name}...")
        if lamp.set_color_hex(hex_code):
            print("✓ Cor definida com sucesso!")
        else:
            print("✗ Erro ao definir cor")
    else:
        print("✗ Opção inválida!")


# ============================================================================
# MENU INTERATIVO
# ============================================================================


def interactive_menu(lamp: SmartLamp):
    """Menu interativo para controlar a lâmpada"""
    
    # Mapeamento de opções para funções
    menu_options = {
        '1': toggle_power,
        '2': set_brightness,
        '3': set_temperature,
        '4': set_color,
        '5': show_status,
        '6': show_debug_menu,
    }
    
    while True:
        print_menu()
        choice = input("Escolha uma opção: ").strip()
        
        if choice == '0':
            print("\n👋 Encerrando...")
            break
        
        elif choice in menu_options:
            # Executa a função correspondente
            menu_options[choice](lamp)

        
        else:
            print("✗ Opção inválida! Tente novamente.")
        
        input("\nPressione ENTER para continuar...")
        clear_screen()


def test_sequence(lamp: SmartLamp):
    """Executa uma sequência de testes de funcionalidades"""
    
    print("1. Testando ligar...")
    lamp.turn_on()
    time.sleep(1)
    
    print("2. Testando brilho máximo...")
    lamp.set_brightness(100)
    time.sleep(1)
    
    print("3. Testando brilho médio...")
    lamp.set_brightness(50)
    time.sleep(1)
    
    print("4. Testando brilho mínimo...")
    lamp.set_brightness(10)
    time.sleep(1)
    
    print("5. Testando modo 'white'...")
    lamp.set_work_mode('white')
    time.sleep(1)
    
    print("6. Testando temperatura fria...")
    lamp.set_temperature(0)
    time.sleep(1)
    
    print("7. Testando temperatura quente...")
    lamp.set_temperature(100)
    time.sleep(1)
    
    print("8. Testando modo 'colour'...")
    lamp.set_work_mode('colour')
    time.sleep(1)
    
    print("9. Desligando...")
    lamp.turn_off()
    
    print("✓ Sequência de testes concluída!")


def main():
    """Função principal"""
    
    clear_screen()
    
    print("=" * 70)
    print("CONTROLE DE LÂMPADA INTELIGENTE TUYA - v0.2")
    print("=" * 70)
    
    # Carrega configurações
    print("\n📂 Carregando configurações dos dispositivos...")
    try:
        devices = load_device_config('devices.json')
        print(f"✓ {len(devices)} dispositivo(s) carregado(s)")
    except FileNotFoundError:
        print("✗ Arquivo devices.json não encontrado!")
        return
    
    # Encontra a lâmpada
    print("\n🔍 Procurando lâmpada 'Quarto Frente'...")
    lamp_config = find_device_by_name(devices, "Quarto Frente")
    
    if not lamp_config:
        print("✗ Lâmpada não encontrada!")
        return
    
    print("✓ Lâmpada encontrada")
    
    # Cria instância da lâmpada
    lamp = SmartLamp(lamp_config, version=3.5)
    
    # Conecta
    print("\n🔌 Conectando ao dispositivo...")
    if not lamp.connect():
        print("✗ Erro ao conectar!")
        return
    
    print("✓ Conectado com sucesso!")
    
    # Menu interativo
    clear_screen()
    interactive_menu(lamp)


if __name__ == "__main__":
    main()
