"""
Script de teste para o novo Wizard Programático (TuyaWizard)
Demonstra como usar a classe TuyaWizard para descobrir dispositivos
sem usar a interface de linha de comando do tinytuya.
"""

import getpass
from tuya_lib import TuyaWizard, DeviceManager

def main():
    print("=== Teste do Wizard Programático ===")
    print("Este script simula o que a interface gráfica fará.\n")

    # 1. Coleta de credenciais (na GUI seriam campos de texto)
    print("Por favor, insira suas credenciais da Tuya IoT Platform:")
    api_key = input("API Key (Access ID): ").strip()
    api_secret = input("API Secret (Access Secret): ").strip()
    region = input("Região (us, eu, cn, in): ").strip()
    device_id = input("Device ID (qualquer um da conta) [Opcional]: ").strip()

    if not (api_key and api_secret and region):
        print("Erro: Credenciais incompletas.")
        return

    # Se device_id for vazio, passa None
    if not device_id:
        device_id = None

    # 2. Inicialização do Wizard
    wizard = TuyaWizard(api_key, api_secret, region, device_id)

    # 3. Conexão e Busca na Nuvem
    print("\n☁️  Conectando à nuvem Tuya...")
    if wizard.connect():
        print("✓ Conectado!")
        
        print("📥 Buscando dispositivos na conta...")
        cloud_devices = wizard.fetch_devices()
        print(f"✓ Encontrados {len(cloud_devices)} dispositivos na nuvem.")
    else:
        print("✗ Falha na conexão.")
        return

    # 4. Busca Local
    print("\n🏠 Escaneando rede local (aguarde 8s)...")
    local_devices = wizard.scan_local()
    print(f"✓ Encontrados {len(local_devices)} dispositivos na rede local.")

    # 5. Combinação de Dados
    print("\n🔄 Combinando dados...")
    merged_devices = wizard.merge_data()
    
    print("\n=== Resultado Final ===")
    for dev in merged_devices:
        status = "Online" if dev['ip'] else "Offline (sem IP)"
        print(f"- {dev['name']} ({dev['id']}): {status}")
        print(f"  Key: {dev['key']}")
        print(f"  IP: {dev['ip']}")
        print("-" * 30)

    # 6. Salvamento (Opcional)
    save = input("\nDeseja salvar estes dispositivos no devices.json? (s/n): ")
    if save.lower() == 's':
        manager = DeviceManager()
        # Backup antes de sobrescrever
        manager.backup_files()
        
        # Atualiza e salva
        manager.devices = merged_devices
        if manager.save_devices():
            print("✓ Dispositivos salvos com sucesso!")
        else:
            print("✗ Erro ao salvar dispositivos.")

if __name__ == "__main__":
    main()
