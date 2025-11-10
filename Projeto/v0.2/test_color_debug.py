"""
    Script de debug para testar envio de cores
    Ajuda a entender qual formato a lâmpada espera
"""

import json
import tinytuya
import time

# Carrega configurações
with open('devices.json', 'r', encoding='utf-8') as f:
    devices = json.load(f)

# Encontra a lâmpada
lamp_config = None
for device in devices:
    if device['name'] == "Quarto Frente":
        lamp_config = device
        break

if not lamp_config:
    print("Lâmpada não encontrada!")
    exit()

print(f"Testando com lâmpada: {lamp_config['name']}")
print(f"ID: {lamp_config['id']}")
print(f"IP: {lamp_config.get('ip')}")

# Cria conexão
device = tinytuya.OutletDevice(
    dev_id=lamp_config['id'],
    address=lamp_config.get('ip'),
    local_key=lamp_config['key'],
    version=3.5
)

# Testa diferentes formatos de cor
print("\n" + "="*60)
print("TESTANDO DIFERENTES FORMATOS DE COR")
print("="*60)

# Formatos a testar
test_colors = [
    ("FF000003e803e8", "Vermelho - formato atual"),
    ("FF0000", "Vermelho - RGB simples"),
    ("0x0000FF", "Azul - com prefixo 0x"),
    ("00FF0003e803e8", "Verde - formato atual"),
]

# Primeiro, muda para modo colour
print("\n1. Mudando para modo 'colour'...")
try:
    result = device.set_value('21', 'colour')
    print(f"   Resultado: {result}")
except Exception as e:
    print(f"   Erro: {e}")

time.sleep(1)

# Testa cada formato
for color_data, description in test_colors:
    print(f"\n2. Testando: {description}")
    print(f"   Enviando DP 24 = {color_data}")
    try:
        result = device.set_value('24', color_data)
        print(f"   Resultado: {result}")
        time.sleep(1)
    except Exception as e:
        print(f"   Erro: {e}")

print("\n" + "="*60)
print("FIM DOS TESTES")
print("="*60)
