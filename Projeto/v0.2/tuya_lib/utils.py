"""
Módulo de utilitários para a biblioteca Tuya

Este módulo contém funções auxiliares para formatação de status,
limpeza de tela e outras operações comuns.
"""

import os


"""
===================
BEGIN Declaração de classes
===================
"""

# Não há classes neste módulo

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

"""
BEGIN clear_screen
 - @retparms : None (limpa a tela do console)
"""
def clear_screen():
    """Limpa a tela do console"""
    os.system('cls' if os.name == 'nt' else 'clear')

"""
END clear_screen
"""

"""
BEGIN format_status_readable
 - @param lamp : Instância da classe SmartLamp para obter status
 - @retparms status_text : String formatada com informações do status da lâmpada
"""
def format_status_readable(lamp) -> str:
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

"""
END format_status_readable
"""

"""
BEGIN is_lamp_online
 - @param device_config : Dicionário com configuração do dispositivo (id, name, key, ip)
 - @param timeout : Tempo máximo de espera para verificação em segundos (padrão: 3)
 - @retparms online : Boolean indicando se o dispositivo está online (True) ou offline (False)
"""
def is_lamp_online(device_config: dict, timeout: int = 3) -> bool:
    """
    Verifica se uma lâmpada está online tentando uma conexão rápida

    Args:
        device_config: Configuração do dispositivo
        timeout: Timeout em segundos

    Returns:
        True se online, False caso contrário
    """
    import socket
    import tinytuya

    try:
        # Verifica se tem IP definido
        address = device_config.get('ip', '').strip()
        if not address:
            return False  # Sem IP, não consegue verificar

        # Tenta criar uma conexão rápida
        device = tinytuya.BulbDevice(
            dev_id=device_config['id'],
            address=address,
            local_key=device_config['key'],
            version=3.5,
            connection_timeout=timeout
        )

        # Tenta obter status
        status = device.status()
        return status is not None and 'Error' not in str(status)

    except (socket.timeout, ConnectionRefusedError, RuntimeError):
        return False
    except Exception:
        return False

"""
END is_lamp_online
"""

"""
===================
END Declaração de funções
===================
"""