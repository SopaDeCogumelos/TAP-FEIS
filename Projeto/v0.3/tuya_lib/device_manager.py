"""
Gerenciador de Dispositivos Tuya
Integra o wizard do tinytuya para descoberta e gerenciamento de dispositivos
"""

import json
import os
import shutil
from datetime import datetime
import tinytuya


"""
===================
BEGIN Declaração de classes
===================
"""

"""
BEGIN DeviceManager
 - @param devices_file : Caminho do arquivo JSON com dispositivos formatados (padrão: 'devices.json')
 - @param tuya_file : Caminho do arquivo JSON de configuração do tinytuya (padrão: 'tinytuya.json')
 - @param raw_file : Caminho do arquivo JSON raw do tinytuya (padrão: 'tuya-raw.json')
 - @var/obj devices_file : Caminho do arquivo de dispositivos
 - @var/obj tuya_file : Caminho do arquivo de configuração tinytuya
 - @var/obj raw_file : Caminho do arquivo raw
 - @var/obj devices : Lista de dispositivos carregados
 - @method __init__ : Inicializa o gerenciador de dispositivos
 - @method load_devices : Carrega dispositivos do arquivo JSON
 - @method save_devices : Salva dispositivos no arquivo JSON
 - @method backup_files : Faz backup dos arquivos de configuração
 - @method run_wizard : Executa o wizard de descoberta de dispositivos
 - @method _clean_wizard_file : Valida e limpa dados do wizard
 - @method sync_from_wizard : Sincroniza dispositivos do wizard
 - @method list_devices : Lista todos os dispositivos
 - @method add_device : Adiciona dispositivo manualmente
 - @method remove_device : Remove um dispositivo
 - @method edit_device : Edita um dispositivo existente
 - @method export_devices : Exporta dispositivos para arquivo
 - @method import_devices : Importa dispositivos de arquivo
 - @retparms : Instância da classe DeviceManager
"""
class DeviceManager:
    """Gerencia os dispositivos Tuya"""

    def __init__(self, devices_file: str = 'devices.json',
                 tuya_file: str = 'tinytuya.json',
                 raw_file: str = 'tuya-raw.json'):
        """
        Inicializa o gerenciador

        Args:
            devices_file: Arquivo com dispositivos formatados
            tuya_file: Arquivo de configuração do tinytuya
            raw_file: Arquivo raw do tinytuya
        """
        self.devices_file = devices_file
        self.tuya_file = tuya_file
        self.raw_file = raw_file
        self.devices = []
        self.load_devices()

    def load_devices(self) -> bool:
        """Carrega os dispositivos do arquivo JSON"""
        try:
            if os.path.exists(self.devices_file):
                with open(self.devices_file, 'r', encoding='utf-8') as f:
                    self.devices = json.load(f)
                return True
            else:
                self.devices = []
                return False
        except Exception as e:
            print(f"Erro ao carregar dispositivos: {e}")
            self.devices = []
            return False

    def save_devices(self) -> bool:
        """Salva os dispositivos no arquivo JSON"""
        try:
            with open(self.devices_file, 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar dispositivos: {e}")
            return False

    def backup_files(self) -> bool:
        """Faz backup dos arquivos de configuração"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup_{timestamp}"

            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            files_to_backup = [
                self.devices_file,
                self.tuya_file,
                self.raw_file
            ]

            for file in files_to_backup:
                if os.path.exists(file):
                    shutil.copy2(file, os.path.join(backup_dir, file))
                    print(f"✓ Backup: {file}")

            print(f"✓ Backup realizado em: {backup_dir}")
            return True
        except Exception as e:
            print(f"Erro ao fazer backup: {e}")
            return False

    def run_wizard(self) -> bool:
        """
        Executa o wizard do tinytuya para descobrir dispositivos (via subprocess)
        Returns:
            True se sucesso, False caso contrário
        """
        import subprocess
        import sys
        print("\n" + "=" * 70)
        print("WIZARD DO TINYTUYA - DESCOBERTA DE DISPOSITIVOS")
        print("=" * 70)
        print("""
Este wizard irá:
1. Procurar por dispositivos Tuya na rede
2. Solicitar chaves de acesso local (Cloud API)
3. Criar/atualizar arquivos de configuração

Certifique-se de:
✓ Ter seus dispositivos Tuya ligados
✓ Estar na mesma rede WiFi dos dispositivos
✓ Ter chaves de acesso local obtidas do app Tuya

DICA: Ao colar dados (API Key, Secret), não copie espaços extras!

Pressione ENTER para continuar ou CTRL+C para cancelar...
""")
        try:
            input()
            # Faz backup antes de rodar o wizard
            print("\n📦 Fazendo backup dos arquivos atuais...")
            self.backup_files()
            # Executa o wizard CLI do tinytuya
            print("\n🔍 Iniciando descoberta de dispositivos...")
            print("Isto pode levar alguns minutos...\n")

            # Obtém o diretório atual para garantir que os arquivos sejam salvos aqui
            current_dir = os.getcwd()

            # Executa o wizard especificando os arquivos de saída
            cmd = [
                sys.executable, "-m", "tinytuya", "wizard",
                "-device-file", self.devices_file,
                "-credentials-file", self.tuya_file,
                "-raw-response-file", self.raw_file
            ]

            result = subprocess.run(cmd, check=False, cwd=current_dir)

            # Valida e limpa o arquivo tinytuya.json após wizard
            if result.returncode == 0 or os.path.exists(self.tuya_file):
                print("\n🧹 Validando e limpando dados do wizard...")
                if self._clean_wizard_file():
                    print("  ✓ Dados validados e limpos")
                else:
                    print("  ⚠️  Aviso: Não foi possível validar completamente")

            if result.returncode != 0:
                print(f"✗ Erro ao executar wizard CLI (código {result.returncode})")
                return False
            print("\n✓ Wizard concluído!")
            print("Os arquivos foram salvos:")
            print(f"  • {self.tuya_file}")
            print(f"  • {self.raw_file}")
            # Sincroniza com o arquivo devices.json
            if self.sync_from_wizard():
                print(f"  • {self.devices_file}")
                return True
            else:
                print("Erro ao sincronizar dispositivos")
                return False
        except KeyboardInterrupt:
            print("\nWizard cancelado pelo usuário")
            return False
        except Exception as e:
            print(f"✗ Erro ao executar wizard: {e}")
            return False

    def _clean_wizard_file(self) -> bool:
        """
        Valida e limpa o arquivo tinytuya.json após o wizard
        Remove espaços em branco dos campos críticos

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.tuya_file):
                return False

            with open(self.tuya_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Campos que devem ter espaços removidos
            critical_fields = ['apiKey', 'apiSecret', 'apiDeviceID', 'apiRegion']

            # Limpa campos críticos na raiz do JSON
            for field in critical_fields:
                if field in data and isinstance(data[field], str):
                    original = data[field]
                    data[field] = data[field].strip()
                    if original != data[field]:
                        print(f"  ✓ Limpeza: {field} (removidos espaços)")

            # Limpa campos críticos em cada dispositivo
            for device_id, device_info in data.items():
                if isinstance(device_info, dict):
                    if 'key' in device_info and isinstance(device_info['key'], str):
                        device_info['key'] = device_info['key'].strip()
                    if 'ip' in device_info and isinstance(device_info['ip'], str):
                        device_info['ip'] = device_info['ip'].strip()

            # Salva o arquivo limpo
            with open(self.tuya_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"  ✗ Erro ao limpar arquivo: {e}")
            return False


    def sync_from_wizard(self) -> bool:
        """
        Sincroniza o devices.json com tinytuya.json do wizard

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.tuya_file):
                print(f"⚠️  Arquivo {self.tuya_file} não encontrado")
                return False

            with open(self.tuya_file, 'r', encoding='utf-8') as f:
                tuya_data = json.load(f)

            # Extrai dispositivos do formato do tinytuya
            new_devices = []
            for device_id, device_info in tuya_data.items():
                if isinstance(device_info, dict) and 'name' in device_info:
                    device = {
                        'id': device_id,
                        'name': device_info.get('name', 'Desconhecido'),
                        'key': device_info.get('key', ''),
                        'ip': device_info.get('ip', ''),
                        'mac': device_info.get('mac', ''),
                        'uuid': device_info.get('uuid', ''),
                        'model': device_info.get('model', ''),
                    }
                    new_devices.append(device)

            if not new_devices:
                print("⚠️  Nenhum dispositivo encontrado no arquivo wizard")
                return False

            # Mescla com dispositivos existentes (evita duplicatas)
            existing_ids = {d['id'] for d in self.devices}
            for new_device in new_devices:
                if new_device['id'] not in existing_ids:
                    self.devices.append(new_device)
                    print(f"  ✓ Novo: {new_device['name']}")
                else:
                    # Atualiza dispositivo existente
                    for existing in self.devices:
                        if existing['id'] == new_device['id']:
                            existing.update(new_device)
                            print(f"  ✓ Atualizado: {new_device['name']}")
                            break

            # Salva
            return self.save_devices()

        except Exception as e:
            print(f"Erro ao sincronizar: {e}")
            return False

    def list_devices(self) -> None:
        """Lista todos os dispositivos"""
        if not self.devices:
            print("Nenhum dispositivo configurado.")
            return

        print("\n╔══════════════════════════════════════════════════════════╗")
        print("║              DISPOSITIVOS CONFIGURADOS                   ║")
        print("╠══════════════════════════════════════════════════════════╣")

        for i, device in enumerate(self.devices, 1):
            ip_display = device.get('ip', '(não definido)')
            status = "✓" if device.get('ip') else "⚠️"

            print(f"║ {i}. {device['name']:35} {status}              ║")
            print(f"║    ID: {device['id']}                  ║")
            print(f"║    IP: {ip_display:20}                         ║")

        print("╚══════════════════════════════════════════════════════════╝\n")

    def add_device(self) -> bool:
        """Adiciona um dispositivo manualmente"""
        print("\n╔════════════════════════════════════════╗")
        print("║      ADICIONAR DISPOSITIVO MANUAL       ║")
        print("╚════════════════════════════════════════╝\n")

        try:
            name = input("Nome do dispositivo: ").strip()
            if not name:
                print("✗ Nome não pode estar vazio")
                return False

            device_id = input("ID do dispositivo (Tuya): ").strip()
            if not device_id:
                print("✗ ID não pode estar vazio")
                return False

            # Verifica se já existe
            if any(d['id'] == device_id for d in self.devices):
                print("✗ Dispositivo com este ID já existe")
                return False

            local_key = input("Chave de acesso local (Key): ").strip()
            if not local_key:
                print("✗ Chave não pode estar vazia")
                return False

            ip_addr = input("Endereço IP (opcional, deixe em branco para 'scan'): ").strip()

            new_device = {
                'id': device_id,
                'name': name,
                'key': local_key,
                'ip': ip_addr,
                'mac': input("Endereço MAC (opcional): ").strip() or '',
                'uuid': input("UUID (opcional): ").strip() or '',
                'model': input("Modelo (opcional): ").strip() or '',
            }

            self.devices.append(new_device)

            if self.save_devices():
                print(f"\n✓ Dispositivo '{name}' adicionado com sucesso!")
                return True
            else:
                print("✗ Erro ao salvar dispositivo")
                return False

        except KeyboardInterrupt:
            print("\n⚠️  Cancelado pelo usuário")
            return False
        except Exception as e:
            print(f"✗ Erro: {e}")
            return False

    def remove_device(self) -> bool:
        """Remove um dispositivo"""
        if not self.devices:
            print("Nenhum dispositivo para remover")
            return False

        self.list_devices()

        try:
            choice = input("Digite o número do dispositivo a remover (0 para cancelar): ").strip()

            if choice == '0':
                return False

            idx = int(choice) - 1
            if 0 <= idx < len(self.devices):
                removed = self.devices.pop(idx)

                if self.save_devices():
                    print(f"\n✓ Dispositivo '{removed['name']}' removido com sucesso!")
                    return True
                else:
                    # Restaura se não conseguiu salvar
                    self.devices.insert(idx, removed)
                    print("✗ Erro ao salvar alterações")
                    return False
            else:
                print("✗ Opção inválida")
                return False

        except ValueError:
            print("✗ Entrada inválida")
            return False

    def edit_device(self) -> bool:
        """Edita um dispositivo existente"""
        if not self.devices:
            print("Nenhum dispositivo para editar")
            return False

        self.list_devices()

        try:
            choice = input("Digite o número do dispositivo a editar (0 para cancelar): ").strip()

            if choice == '0':
                return False

            idx = int(choice) - 1
            if 0 <= idx < len(self.devices):
                device = self.devices[idx]

                print(f"\n📝 Editando: {device['name']}")
                print("(deixe em branco para manter o valor atual)\n")

                new_name = input(f"Nome [{device['name']}]: ").strip()
                if new_name:
                    device['name'] = new_name

                new_ip = input(f"IP [{device.get('ip', '')}]: ").strip()
                if new_ip is not None:
                    device['ip'] = new_ip

                new_key = input(f"Chave [{device['key'][:5]}...]: ").strip()
                if new_key:
                    device['key'] = new_key

                if self.save_devices():
                    print(f"\n✓ Dispositivo '{device['name']}' atualizado com sucesso!")
                    return True
                else:
                    print("✗ Erro ao salvar alterações")
                    return False
            else:
                print("✗ Opção inválida")
                return False

        except ValueError:
            print("✗ Entrada inválida")
            return False

    def export_devices(self, filename: str = None) -> bool:
        """Exporta dispositivos para um arquivo JSON"""
        if not filename:
            filename = f"devices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, indent=4, ensure_ascii=False)
            print(f"✓ Dispositivos exportados para: {filename}")
            return True
        except Exception as e:
            print(f"✗ Erro ao exportar: {e}")
            return False

    def import_devices(self, filename: str) -> bool:
        """Importa dispositivos de um arquivo JSON"""
        try:
            if not os.path.exists(filename):
                print(f"✗ Arquivo não encontrado: {filename}")
                return False

            with open(filename, 'r', encoding='utf-8') as f:
                imported = json.load(f)

            if not isinstance(imported, list):
                print("✗ Formato inválido (deve ser uma lista de dispositivos)")
                return False

            # Mescla com existentes
            existing_ids = {d['id'] for d in self.devices}
            added = 0

            for device in imported:
                if device.get('id') not in existing_ids:
                    self.devices.append(device)
                    added += 1

            if self.save_devices():
                print(f"✓ {added} dispositivo(s) importado(s)")
                return True
            else:
                print("✗ Erro ao salvar dispositivos")
                return False

        except Exception as e:
            print(f"✗ Erro ao importar: {e}")
            return False

"""
END DeviceManager
"""

"""
===================
END Declaração de classes
===================
"""


"""
===================
BEGIN Declaração de funções
===================
"""

# Não há funções fora das classes neste módulo

"""
===================
END Declaração de funções
===================
"""