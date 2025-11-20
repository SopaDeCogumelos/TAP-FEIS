# Projeto JarVision - Gerenciamento de Dispositivos IoT

Este diretório contém o desenvolvimento progressivo do Projeto Final da disciplina. O objetivo é criar um sistema de controle para dispositivos de casa inteligente (Smart Home) utilizando Python, com foco em dispositivos do ecossistema Tuya.

## Estrutura de Versões

### [v0.4](./v0.4/) - Versão Atual (Estável)
- **Interface Gráfica (GUI):** Implementada com Kivy.
- **Funcionalidades:** Controle de cor, brilho, temperatura, On/Off.
- **Gerenciamento:** Scanner de rede, adição manual e edição de dispositivos.
- **Arquitetura:** Separação clara entre UI (`main_gui.py`) e Backend (`tuya_lib`).

### [v0.3](./v0.3/) - Transição
- Versão intermediária onde o desenvolvimento da GUI foi iniciado.
- Contém correções de bugs da v0.2.

### [v0.2](./v0.2/) - CLI Avançada
- **Interface:** Menu interativo via linha de comando (Terminal).
- **Persistência:** Introdução do `devices.json` para salvar configurações.
- **Protocolo:** Suporte aprimorado ao protocolo Tuya v3.5.

### [v0.1](./v0.1/) - Modularização
- Primeira refatoração do código em classes (`SmartLamp`, `TuyaDevice`).
- Separação da lógica de conexão.

### [v0.0](./v0.0/) - Prova de Conceito
- Scripts iniciais para teste de conexão e comandos básicos.
- Testes com bibliotecas `tinytuya`.

## Como Executar

Recomendamos utilizar a versão mais recente (**v0.4**).

1. Navegue até a pasta da versão:
   ```bash
   cd v0.4
   ```
2. Siga as instruções no `README.md` específico daquela versão.

## Tecnologias Principais
- **Linguagem:** Python 3.x
- **GUI:** Kivy
- **IoT:** tinytuya (Tuya Protocol)
