import socket
import tinytuya
import time

TARGET_IP = "192.168.1.6"
PORTS = [6668, 6666, 6667]

print(f"=== Teste de Conectividade Local para {TARGET_IP} ===")

# 1. Teste de TCP (Porta 6668)
print(f"\n1. Testando conexão TCP na porta 6668 (Controle)...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex((TARGET_IP, 6668))
    if result == 0:
        print(f"   ✓ Porta 6668 ABERTA - Dispositivo acessível via TCP")
    else:
        print(f"   ✗ Porta 6668 FECHADA/FILTRADA (Código: {result})")
    sock.close()
except Exception as e:
    print(f"   ✗ Erro ao testar TCP: {e}")

# 2. Teste de UDP Broadcast (Simulação)
print(f"\n2. Testando tinytuya.deviceScan(forcescan=True)...")
try:
    # forcescan=True envia pacotes de descoberta mesmo se não ouvir nada
    devices = tinytuya.deviceScan(forcescan=True, verbose=True)
    print(f"   Dispositivos encontrados: {len(devices)}")
    for d in devices:
        print(f"   - IP: {d.get('ip')} | ID: {d.get('id') or d.get('gwId')}")
except Exception as e:
    print(f"   ✗ Erro no deviceScan: {e}")

print("\n=== Fim do Teste ===")
