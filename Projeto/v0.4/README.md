"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Aluno: Luis Felipe Marcon Brunhara
    Git: https://github.com/SopaDeCogumelos/TAP-FEIS

    Projeto Final - Gerenciamento de Dispositivos IoT - v0.4
"""

# Projeto JarVision v0.4

Sistema de gerenciamento e controle de dispositivos IoT Tuya (Lâmpadas Inteligentes) com interface gráfica moderna desenvolvida em Kivy.

## Sobre o Projeto

O **Projeto JarVision** é uma aplicação Python desenvolvida para a disciplina de Tópicos Avançados de Programação (TAP-FEIS). O objetivo é permitir o controle local de dispositivos inteligentes Tuya sem depender da nuvem, garantindo maior privacidade e velocidade de resposta.

A versão **v0.4** introduz uma interface gráfica completa (GUI), substituindo o antigo menu de linha de comando (CLI), e adiciona funcionalidades avançadas de gerenciamento.

## Funcionalidades

### Controle de Dispositivos
- **Interface Gráfica**: Controle intuitivo via Kivy.
- **Liga/Desliga**: Controle de energia instantâneo.
- **Brilho e Temperatura**: Sliders para ajuste fino de intensidade e temperatura de cor.
- **Cores RGB**: Seletor de cores completo para lâmpadas RGB.
- **Feedback Visual**: Status de conexão e estado atual do dispositivo em tempo real.

### Gerenciamento (Admin)
- **Scanner de Rede**: Descoberta automática de dispositivos Tuya na rede local.
- **Edição de Dispositivos**: Altere nome, IP, ID e Chave Local diretamente na interface.
- **Adição Manual**: Cadastro de dispositivos offline ou não detectados.
- **Persistência**: Dados salvos automaticamente em `devices.json`.

## Tecnologias Utilizadas

- **Python 3.x**: Linguagem base.
- **Kivy**: Framework para desenvolvimento da Interface Gráfica (GUI).
- **tinytuya**: Biblioteca para comunicação com protocolo Tuya (v3.1, v3.3, v3.5).
- **JSON**: Armazenamento de configurações e dados dos dispositivos.

## Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SopaDeCogumelos/TAP-FEIS.git
   cd TAP-FEIS/Projeto/v0.4
   ```

2. **Crie e ative um ambiente virtual (recomendado):**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
   *Nota: Certifique-se de que o Kivy foi instalado corretamente para o seu sistema operacional.*

## 🚀 Como Usar

1. **Execute a aplicação:**
   ```bash
   python main_gui.py
   ```

2. **Primeiros Passos:**
   - Ao abrir, você verá o **Dashboard** com os dispositivos cadastrados.
   - Se não houver dispositivos, vá em **Config (Admin)**.
   - Use o botão **"Escanear Rede"** para encontrar lâmpadas automaticamente ou **"Adicionar Manual"** se já tiver as chaves.
   - Clique em **"Controlar"** no card de um dispositivo para acessar o painel de controle.

## Estrutura do Projeto

```
v0.4/
├── main_gui.py           # Aplicação Principal (GUI Kivy)
├── main.py               # Versão CLI (Legado)
├── devices.json          # Banco de dados de dispositivos
├── requirements.txt      # Dependências do projeto
├── tuya_lib/             # Biblioteca Core
│   ├── smart_lamp.py     # Lógica de controle da lâmpada
│   ├── device_manager.py # Gerenciamento de arquivos e dados
│   └── ...
└── ...
```

## Notas de Versão (v0.4)

- **Novo:** Interface Gráfica (GUI) com Kivy.
- **Novo:** Funcionalidade de "Editar Dispositivo" no painel Admin.
- **Melhoria:** Correção no mapeamento de DPs (Data Points) para garantir funcionamento do botão On/Off em diversos modelos de lâmpada.
- **Melhoria:** Renomeação do projeto para "Projeto JarVision".

---
**Disciplina:** Tópicos Avançados de Programação  
**Professor:** Christiane Marie Schweitzer  
**Alunos:** 
    - Arthur de Souza Leite
    - Luis Felipe Marcon Brunhara
    - Luiz Felipe Moura Tarifa