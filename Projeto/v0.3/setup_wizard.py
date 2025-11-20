import subprocess
import json
import os
import sys

def run_wizard_automated(config_file='tinytuya.json.backup'):
    """
    Executa o wizard oficial do tinytuya usando as credenciais do arquivo fornecido.
    """
    if not os.path.exists(config_file):
        print(f"Erro: Arquivo de configuração '{config_file}' não encontrado.")
        return

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print(f"Erro: Arquivo '{config_file}' não é um JSON válido.")
        return

    api_key = config.get('apiKey')
    api_secret = config.get('apiSecret')
    region = config.get('apiRegion')
    device_id = config.get('apiDeviceID')

    if not all([api_key, api_secret, region, device_id]):
        print("Erro: Faltam credenciais no arquivo de configuração.")
        print(f"Necessário: apiKey, apiSecret, apiRegion, apiDeviceID")
        print(f"Encontrado: {list(config.keys())}")
        return

    if device_id == "scan":
        print("Aviso: 'apiDeviceID' é 'scan'. Tentando encontrar um ID válido em backups...")
        
        # Tenta encontrar em tuya-raw.json.backup
        raw_backup = os.path.join(os.path.dirname(config_file), 'tuya-raw.json.backup')
        if os.path.exists(raw_backup):
            try:
                with open(raw_backup, 'r') as f:
                    raw_data = json.load(f)
                    if 'result' in raw_data and len(raw_data['result']) > 0:
                        found_id = raw_data['result'][0]['id']
                        print(f"Encontrado ID no backup: {found_id}")
                        device_id = found_id
                        # Opcional: Atualizar o arquivo de config
            except Exception as e:
                print(f"Erro ao ler backup: {e}")
        
        if device_id == "scan":
            print("Erro: Não foi possível encontrar um Device ID válido.")
            print("Por favor, edite o arquivo tinytuya.json.backup e coloque um ID de dispositivo válido.")
            return

    print(f"Iniciando tinytuya wizard com:")
    print(f"  Region: {region}")
    print(f"  Device ID: {device_id}")
    print(f"  Key: {api_key[:4]}...{api_key[-4:]}")
    
    # Constrói o comando
    # python -m tinytuya wizard -key ... -secret ... -region ... -device ... -yes
    cmd = [
        sys.executable, "-m", "tinytuya", "wizard",
        "-key", api_key,
        "-secret", api_secret,
        "-region", region,
        "-device", device_id,
        "-yes",
        "-nocolor" # Para evitar caracteres de escape no log se for capturado
    ]

    try:
        # Executa o comando e espera terminar
        subprocess.run(cmd, check=True)
        print("\nWizard concluído com sucesso!")
        print("Arquivos gerados: devices.json, tinytuya.json, tuya-raw.json")
    except subprocess.CalledProcessError as e:
        print(f"\nErro ao executar o wizard: {e}")
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")

if __name__ == "__main__":
    # Ajusta o caminho se rodar da raiz ou da pasta v0.2
    if os.path.exists("tinytuya.json.backup"):
        run_wizard_automated("tinytuya.json.backup")
    elif os.path.exists("Projeto/v0.2/tinytuya.json.backup"):
        run_wizard_automated("Projeto/v0.2/tinytuya.json.backup")
    else:
        # Tenta caminho absoluto baseado no script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "tinytuya.json.backup")
        if os.path.exists(config_path):
            run_wizard_automated(config_path)
        else:
            print("Não foi possível encontrar tinytuya.json.backup")
