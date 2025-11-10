"""
Módulo contendo a classe base para todos os dispositivos IoT.
"""

class Device:
    """
    Classe base para representar um dispositivo IoT genérico.
    """
    def __init__(self, name, device_type, status="unknown"):
        """
        Inicializa um dispositivo com nome, tipo e status.
        """
        self.name = name
        self.device_type = device_type
        self.status = status

    def to_dict(self):
        """
        Converte os atributos do dispositivo para um dicionário.
        """
        return {
            "name": self.name,
            "device_type": self.device_type,
            "status": self.status
        }
