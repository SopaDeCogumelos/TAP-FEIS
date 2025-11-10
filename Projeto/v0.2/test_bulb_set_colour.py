"""
    Script de teste para set_colour do BulbDevice
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

# Cria conexão usando BulbDevice
device = tinytuya.BulbDevice(
    dev_id=lamp_config['id'],
    address=lamp_config.get('ip'),
    local_key=lamp_config['key'],
    version=3.5
)

print("\n" + "="*60)
print("TESTANDO set_colour DO BULBDEVICE")
print("="*60)

# Primeiro, muda para modo colour
print("\n1. Mudando para modo 'colour'...")
try:
    result = device.set_mode('colour')
    print(f"   Resultado: {result}")
except Exception as e:
    print(f"   Erro: {e}")

time.sleep(1)

# Testa cores usando set_colour
test_colors = [
    (255, 0, 0, "Vermelho"),
    (0, 255, 0, "Verde"),
    (0, 0, 255, "Azul"),
    (255, 255, 0, "Amarelo"),
    (255, 0, 255, "Magenta"),
]

for r, g, b, name in test_colors:
    print(f"\n2. Testando: {name} RGB({r}, {g}, {b})")
    try:
        result = device.set_colour(r, g, b, nowait=False)
        print(f"   Resultado: {result}")
        time.sleep(1)
    except Exception as e:
        print(f"   Erro: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("FIM DOS TESTES")
print("="*60)
