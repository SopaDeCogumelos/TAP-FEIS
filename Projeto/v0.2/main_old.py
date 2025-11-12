"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara
    Git: https://github.com/SopaDeCogumelos/TAP-FEIS

    Projeto Final - Gerenciamento de Dispositivos IoT - v0.2

    Controle de lâmpada Tuya com interface interativa

"""

import time
from tuya_lib import (
    SmartLamp, DeviceManager,
    load_device_config, find_device_by_name,
    clear_screen, format_status_readable, is_lamp_online
)


def print_menu(current_lamp_name: str = ""):
    """Exibe o menu principal"""
    lamp_info = f" ({current_lamp_name})" if current_lamp_name else ""
    print(f"""
╔═════════════════════════════════════════╗
║ CONTROLE DE LÂMPADA INTELIGENTE{lamp_info}
╠═════════════════════════════════════════╣
║  1. Liga/Desliga                        ║
║  2. Ajustar brilho                      ║
║  3. Ajustar temperatura                 ║
║  4. Configurar cor                      ║
║  5. Ver status                          ║
║  6. Debug                               ║
║  7. Trocar Lâmpada                      ║
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


def show_status(lamp: SmartLamp):
    """Opção 5: Mostra o status da lâmpada"""
    print("\n📊 Obtendo status da lâmpada...")
    status_text = format_status_readable(lamp)
    print(status_text)


def set_brightness(lamp: SmartLamp):
    """Opção 2: Ajusta o brilho da lâmpada"""
    try:
        current_value = input("Digite o brilho desejado (0-100%): ").strip()
        value = int(current_value)

        if 0 <= value <= 100:
            print(f"\n💡 Ajustando brilho para {value}%...")
            if lamp.set_brightness(value):
                print("✓ Brilho ajustado com sucesso!")
            else:
                print("✗ Erro ao ajustar brilho")
        else:
            print("✗ Valor deve estar entre 0 e 100!")

    except ValueError:
        print("✗ Valor inválido! Digite um número entre 0 e 100.")


def set_temperature(lamp: SmartLamp):
    """Opção 3: Ajusta a temperatura da cor"""
    try:
        current_value = input("Digite a temperatura desejada (0-100%): ").strip()
        value = int(current_value)

        if 0 <= value <= 100:
            print(f"\n🌡️  Ajustando temperatura para {value}%...")
            if lamp.set_temperature(value):
                print("✓ Temperatura ajustada com sucesso!")
            else:
                print("✗ Erro ao ajustar temperatura")
        else:
            print("✗ Valor deve estar entre 0 e 100!")

    except ValueError:
        print("✗ Valor inválido! Digite um número entre 0 e 100.")


def set_color(lamp: SmartLamp):
    """Opção 4: Configura a cor da lâmpada"""
    print("""
╔═════════════════════════════════════════╗
║           CONFIGURAR COR               ║
╠═════════════════════════════════════════╣
║  1. Por código hexadecimal (ex: FF0000)║
║  2. Por valores RGB (0-255)            ║
║  3. Cores predefinidas                  ║
║  0. Voltar                              ║
╚═════════════════════════════════════════╝
""")

    choice = input("Escolha uma opção: ").strip()

    if choice == "1":
        set_color_by_hex(lamp)
    elif choice == "2":
        set_color_by_rgb(lamp)
    elif choice == "3":
        set_color_by_preset(lamp)
    elif choice == "0":
        return
    else:
        print("✗ Opção inválida!")


def print_debug_menu():
    """Exibe o menu de debug"""
    print("""
╔═════════════════════════════════════════╗
║              MENU DEBUG                ║
╠═════════════════════════════════════════╣
║  1. Informações do dispositivo         ║
║  2. Sequência de teste                 ║
║  0. Voltar                              ║
╚═════════════════════════════════════════╝
""")


def show_debug_menu(lamp: SmartLamp):
    """Opção 6: Menu de debug"""
    while True:
        print_debug_menu()
        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            print(lamp.get_info())
            input("\nPressione ENTER para continuar...")
        elif choice == "2":
            test_sequence(lamp)
        elif choice == "0":
            break
        else:
            print("✗ Opção inválida!")
            time.sleep(1)

        clear_screen()


def set_color_by_hex(lamp: SmartLamp):
    """Define cor por código hexadecimal"""
    hex_color = input("Digite o código hexadecimal (ex: FF0000): ").strip()

    print(f"\n🎨 Configurando cor #{hex_color}...")
    if lamp.set_color_hex(hex_color):
        print("✓ Cor configurada com sucesso!")
    else:
        print("✗ Erro ao configurar cor")


def set_color_by_rgb(lamp: SmartLamp):
    """Define cor por valores RGB"""
    try:
        r = int(input("Vermelho (0-255): ").strip())
        g = int(input("Verde (0-255): ").strip())
        b = int(input("Azul (0-255): ").strip())

        print(f"\n🎨 Configurando cor RGB({r}, {g}, {b})...")
        if lamp.set_color_rgb(r, g, b):
            print("✓ Cor configurada com sucesso!")
        else:
            print("✗ Erro ao configurar cor")

    except ValueError:
        print("✗ Valores inválidos! Digite números entre 0 e 255.")


def set_color_by_preset(lamp: SmartLamp):
    """Define cor por predefinições"""
    presets = {
        "1": ("Vermelho", "FF0000"),
        "2": ("Verde", "00FF00"),
        "3": ("Azul", "0000FF"),
        "4": ("Amarelo", "FFFF00"),
        "5": ("Ciano", "00FFFF"),
        "6": ("Magenta", "FF00FF"),
        "7": ("Branco", "FFFFFF"),
        "8": ("Laranja", "FFA500"),
        "9": ("Rosa", "FFC0CB"),
        "10": ("Roxo", "800080")
    }

    print("""
╔═════════════════════════════════════════╗
║            CORES PREDEFINIDAS          ║
╠═════════════════════════════════════════╣""")

    for key, (name, hex_code) in presets.items():
        print(f"║  {key}. {name:<12} (#{hex_code})             ║")

    print("""║  0. Voltar                              ║
╚═════════════════════════════════════════╝
""")

    choice = input("Escolha uma cor: ").strip()

    if choice in presets:
        name, hex_code = presets[choice]
        print(f"\n🎨 Configurando cor {name} (#{hex_code})...")
        if lamp.set_color_hex(hex_code):
            print("✓ Cor configurada com sucesso!")
        else:
            print("✗ Erro ao configurar cor")
    elif choice == "0":
        return
    else:
        print("✗ Opção inválida!")


def select_lamp_menu(devices: list) -> dict:
    """Menu para seleção de lâmpada"""
    while True:
        clear_screen()
        print("""
╔═════════════════════════════════════════╗
║         SELEÇÃO DE LÂMPADA             ║
╠═════════════════════════════════════════╣""")

        if not devices:
            print("""║  Nenhum dispositivo encontrado!        ║
║                                         ║
║  Use o menu de gerenciamento para       ║
║  adicionar dispositivos.                ║
╚═════════════════════════════════════════╝""")
            input("\nPressione ENTER para continuar...")
            return None

        # Lista dispositivos com status online/offline
        for i, device in enumerate(devices, 1):
            name = device['name']
            ip = device.get('ip', 'N/A')
            online = is_lamp_online(device)
            status = "✓ Online" if online else "✗ Offline"
            print(f"║  {i}. {name:<15} IP: {ip:<15} {status:<9} ║")

        print("""║                                         ║
║  0. Voltar                               ║
╚═════════════════════════════════════════╝
""")

        choice = input("Escolha uma lâmpada: ").strip()

        if choice == "0":
            return None
        elif choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(devices):
                selected_device = devices[index]
                print(f"\n🔌 Selecionada: {selected_device['name']}")
                return selected_device
            else:
                print("✗ Número inválido!")
        else:
            print("✗ Opção inválida!")

        time.sleep(1)


def interactive_menu(lamp: SmartLamp, devices: list = None):
    """Menu interativo para controle da lâmpada"""
    current_lamp_name = lamp.config['name'] if lamp else ""

    while True:
        clear_screen()
        print_menu(current_lamp_name)

        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            toggle_power(lamp)
        elif choice == "2":
            set_brightness(lamp)
        elif choice == "3":
            set_temperature(lamp)
        elif choice == "4":
            set_color(lamp)
        elif choice == "5":
            show_status(lamp)
        elif choice == "6":
            show_debug_menu(lamp)
        elif choice == "7":
            # Trocar lâmpada
            new_device = select_lamp_menu(devices)
            if new_device:
                print(f"\n🔄 Trocando para lâmpada: {new_device['name']}")
                new_lamp = SmartLamp(new_device)
                if new_lamp.connect():
                    lamp = new_lamp
                    current_lamp_name = lamp.config['name']
                    print("✓ Conectado com sucesso!")
                else:
                    print("✗ Erro ao conectar à nova lâmpada")
            else:
                print("Nenhuma lâmpada selecionada")
        elif choice == "0":
            break
        else:
            print("✗ Opção inválida!")

        if choice != "0":
            input("\nPressione ENTER para continuar...")

    return lamp


def test_sequence(lamp: SmartLamp):
    """Executa uma sequência de teste na lâmpada"""
    print("\n🧪 Iniciando sequência de teste...")

    # Teste 1: Status
    print("1. Testando obtenção de status...")
    status = lamp.get_status()
    if status:
        print("   ✓ Status obtido com sucesso")
    else:
        print("   ✗ Erro ao obter status")
        return

    # Teste 2: Ligar
    print("2. Testando ligar lâmpada...")
    if lamp.turn_on():
        print("   ✓ Lâmpada ligada")
        time.sleep(1)
    else:
        print("   ✗ Erro ao ligar")
        return

    # Teste 3: Brilho
    print("3. Testando ajuste de brilho...")
    if lamp.set_brightness(50):
        print("   ✓ Brilho ajustado para 50%")
        time.sleep(1)
    else:
        print("   ✗ Erro ao ajustar brilho")

    # Teste 4: Cor
    print("4. Testando mudança de cor...")
    if lamp.set_color_hex("FF0000"):
        print("   ✓ Cor mudada para vermelho")
        time.sleep(1)
    else:
        print("   ✗ Erro ao mudar cor")

    # Teste 5: Temperatura
    print("5. Testando ajuste de temperatura...")
    if lamp.set_temperature(75):
        print("   ✓ Temperatura ajustada para 75%")
        time.sleep(1)
    else:
        print("   ✗ Erro ao ajustar temperatura")

    # Teste 6: Desligar
    print("6. Testando desligar lâmpada...")
    if lamp.turn_off():
        print("   ✓ Lâmpada desligada")
    else:
        print("   ✗ Erro ao desligar")

    print("\n✓ Sequência de teste concluída!")


def print_admin_menu():
    """Exibe o menu de administração"""
    print("""
╔═════════════════════════════════════════╗
║       GERENCIAMENTO DE DISPOSITIVOS    ║
╠═════════════════════════════════════════╣
║  1. Executar wizard de descoberta      ║
║  2. Adicionar dispositivo manualmente  ║
║  3. Listar dispositivos                ║
║  4. Editar dispositivo                 ║
║  5. Remover dispositivo                ║
║  6. Exportar dispositivos              ║
║  7. Importar dispositivos              ║
║  0. Voltar                             ║
╚═════════════════════════════════════════╝
""")


def admin_menu(manager: DeviceManager) -> None:
    """Menu de administração de dispositivos"""
    while True:
        clear_screen()
        print_admin_menu()

        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            # Executar wizard
            if manager.run_wizard():
                print("\n✓ Wizard executado com sucesso!")
            else:
                print("\n✗ Erro ao executar wizard")
        elif choice == "2":
            # Adicionar dispositivo
            if manager.add_device():
                print("\n✓ Dispositivo adicionado com sucesso!")
            else:
                print("\n✗ Erro ao adicionar dispositivo")
        elif choice == "3":
            # Listar dispositivos
            manager.list_devices()
        elif choice == "4":
            # Editar dispositivo
            if manager.edit_device():
                print("\n✓ Dispositivo editado com sucesso!")
            else:
                print("\n✗ Erro ao editar dispositivo")
        elif choice == "5":
            # Remover dispositivo
            if manager.remove_device():
                print("\n✓ Dispositivo removido com sucesso!")
            else:
                print("\n✗ Erro ao remover dispositivo")
        elif choice == "6":
            # Exportar
            if manager.export_devices():
                print("\n✓ Dispositivos exportados com sucesso!")
            else:
                print("\n✗ Erro ao exportar dispositivos")
        elif choice == "7":
            # Importar
            filename = input("Nome do arquivo a importar: ").strip()
            if not filename:
                print("✗ Nome do arquivo é obrigatório!")
            elif manager.import_devices(filename):
                print("\n✓ Dispositivos importados com sucesso!")
            else:
                print("\n✗ Erro ao importar dispositivos")
        elif choice == "0":
            break
        else:
            print("✗ Opção inválida!")

        if choice != "0":
            input("\nPressione ENTER para continuar...")


def print_main_menu():
    """Exibe o menu inicial"""
    print("""
╔═════════════════════════════════════════╗
║    CONTROLE DE LÂMPADA INTELIGENTE      ║
║          Tuya - v0.2                    ║
╠═════════════════════════════════════════╣
║  1. Controlar Lâmpada                   ║
║  2. Gerenciar Dispositivos              ║
║  0. Sair                                ║
╚═════════════════════════════════════════╝
""")


def control_lamp(manager: DeviceManager) -> None:
    """Função principal para controle de lâmpada"""
    # Carrega dispositivos
    devices = manager.devices
    if not devices:
        print("❌ Nenhum dispositivo encontrado!")
        print("Use o menu de gerenciamento para adicionar dispositivos.")
        return

    # Seleciona lâmpada
    device = select_lamp_menu(devices)
    if not device:
        return

    # Cria instância da lâmpada
    lamp = SmartLamp(device)

    # Conecta à lâmpada
    print(f"\n🔌 Conectando à lâmpada '{device['name']}'...")
    if not lamp.connect():
        print("❌ Erro ao conectar à lâmpada!")
        return

    print("✅ Conectado com sucesso!")

    # Menu interativo
    interactive_menu(lamp, devices)


def main():
    """Função principal"""
    print("""
======================================================================
CONTROLE DE LÂMPADA INTELIGENTE TUYA - v0.2
======================================================================
""")

    # Inicializa gerenciador de dispositivos
    manager = DeviceManager('devices.json', 'tinytuya.json', 'tuya-raw.json')

    while True:
        clear_screen()
        print_main_menu()

        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            control_lamp(manager)
        elif choice == "2":
            admin_menu(manager)
        elif choice == "0":
            print("\n👋 Até logo!")
            break
        else:
            print("✗ Opção inválida!")

        if choice != "0":
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()