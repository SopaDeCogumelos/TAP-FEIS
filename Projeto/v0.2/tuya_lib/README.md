# Biblioteca Tuya IoT

Biblioteca Python para controle de dispositivos IoT Tuya, com foco em lâmpadas inteligentes.

## Estrutura

```
tuya_lib/
├── __init__.py          # Interface principal da biblioteca
├── smart_lamp.py        # Classe SmartLamp para controle de lâmpadas
├── device_manager.py    # Classe DeviceManager para gerenciamento de dispositivos
└── utils.py             # Funções utilitárias
```

## Instalação

A biblioteca está localizada na pasta `tuya_lib` e pode ser importada diretamente:

```python
from tuya_lib import SmartLamp, DeviceManager
```

## Dependências

- `tinytuya` - Biblioteca para comunicação com dispositivos Tuya
- `json` - Manipulação de arquivos JSON (padrão do Python)
- `os`, `socket`, `time` - Módulos padrão do Python

## Uso Básico

### Controle de Lâmpada

```python
from tuya_lib import SmartLamp

# Configuração do dispositivo
device_config = {
    'id': 'ebecbc6d2743ca812dzudh',
    'name': 'Quarto Frente',
    'key': 'SJ*:Nn{{+VN2kH3^',
    'ip': '192.168.1.6'
}

# Criar instância da lâmpada
lamp = SmartLamp(device_config)

# Conectar
if lamp.connect():
    # Controlar a lâmpada
    lamp.turn_on()
    lamp.set_brightness(75)
    lamp.set_color_hex('FF0000')  # Vermelho
    lamp.turn_off()
```

### Gerenciamento de Dispositivos

```python
from tuya_lib import DeviceManager

# Criar gerenciador
manager = DeviceManager('devices.json', 'tinytuya.json', 'tuya-raw.json')

# Carregar dispositivos
manager.load_devices()

# Executar wizard de descoberta
manager.run_wizard()

# Listar dispositivos
manager.list_devices()
```

## Classes Principais

### SmartLamp

Classe para controle de lâmpadas inteligentes Tuya.

**Métodos principais:**
- `connect(timeout=5)` - Conecta ao dispositivo
- `turn_on()` / `turn_off()` - Liga/desliga
- `set_brightness(value)` - Ajusta brilho (0-100%)
- `set_temperature(value)` - Ajusta temperatura (0-100%)
- `set_color_hex(hex_color)` - Define cor por hexadecimal
- `set_color_rgb(r, g, b)` - Define cor por RGB
- `get_status()` - Obtém status atual
- `get_info()` - Informações do dispositivo

### DeviceManager

Classe para gerenciamento de dispositivos Tuya.

**Métodos principais:**
- `load_devices()` - Carrega dispositivos do arquivo
- `save_devices()` - Salva dispositivos no arquivo
- `run_wizard()` - Executa wizard de descoberta
- `add_device()` - Adiciona dispositivo manualmente
- `edit_device()` - Edita dispositivo existente
- `remove_device()` - Remove dispositivo
- `list_devices()` - Lista todos os dispositivos
- `export_devices(filename)` - Exporta dispositivos
- `import_devices(filename)` - Importa dispositivos

## Funções Utilitárias

- `clear_screen()` - Limpa tela do console
- `format_status_readable(lamp)` - Formata status da lâmpada
- `is_lamp_online(device_config)` - Verifica se dispositivo está online
- `load_device_config(filename)` - Carrega configuração de arquivo
- `find_device_by_name(devices, name)` - Encontra dispositivo por nome
- `get_dp_from_mapping(device, code)` - Extrai Data Point do mapeamento

## Formato dos Arquivos

### devices.json
Arquivo principal com dispositivos configurados:

```json
[
  {
    "id": "ebecbc6d2743ca812dzudh",
    "name": "Quarto Frente",
    "key": "SJ*:Nn{{+VN2kH3^",
    "ip": "192.168.1.6",
    "model": "10W"
  }
]
```

### tinytuya.json
Arquivo de credenciais gerado pelo wizard:

```json
{
  "apiKey": "your_api_key",
  "apiSecret": "your_api_secret",
  "apiRegion": "us",
  "device_id": {
    "id": "ebecbc6d2743ca812dzudh",
    "key": "SJ*:Nn{{+VN2kH3^",
    "ip": "192.168.1.6"
  }
}
```

## Tratamento de Erros

A biblioteca inclui tratamento robusto de erros:

- **Timeout de conexão** - Dispositivos offline
- **Erros de autenticação** - Chaves inválidas
- **Erros de rede** - Problemas de conectividade
- **Validação de entrada** - Dados malformados

## Exemplo Completo

```python
from tuya_lib import SmartLamp, DeviceManager, format_status_readable

# Gerenciamento de dispositivos
manager = DeviceManager()
manager.load_devices()

# Selecionar primeira lâmpada
if manager.devices:
    device = manager.devices[0]
    lamp = SmartLamp(device)

    if lamp.connect():
        print("Conectado!")

        # Operações
        lamp.turn_on()
        lamp.set_brightness(80)
        lamp.set_color_hex('00FF00')  # Verde

        # Status
        print(format_status_readable(lamp))

        lamp.turn_off()
```

## Desenvolvimento

Para modificar a biblioteca:

1. Edite os arquivos em `tuya_lib/`
2. Teste as mudanças no `main.py`
3. Mantenha a compatibilidade da API pública
4. Atualize este README conforme necessário

## Licença

Este projeto é parte do trabalho acadêmico da disciplina TAP-FEIS.