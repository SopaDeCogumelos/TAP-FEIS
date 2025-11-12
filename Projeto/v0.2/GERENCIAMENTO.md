# Sistema de Gerenciamento de Dispositivos Tuya - v0.2

## 📋 Funcionalidades

### 1. **Controlar Lâmpada**
   - Ligar/Desligar
   - Ajustar brilho (0-100%)
   - Ajustar temperatura (0-100%)
   - Configurar cores (Hex, RGB, Pré-definidas)
   - Ver status formatado
   - Menu de debug
   - Trocar lâmpada em tempo real

### 2. **Gerenciar Dispositivos**
   - **Executar Wizard**: Descobrir novos dispositivos Tuya automaticamente
   - **Listar**: Ver todos os dispositivos configurados
   - **Adicionar**: Adicionar dispositivo manualmente
   - **Editar**: Atualizar informações de um dispositivo
   - **Remover**: Deletar um dispositivo
   - **Exportar**: Salvar lista de dispositivos em arquivo JSON
   - **Importar**: Carregar dispositivos de um arquivo externo
   - **Backup**: Fazer backup automático dos arquivos de configuração

## 🚀 Como Usar

### Primeira Execução

```bash
python main.py
```

Menu Inicial:
```
CONTROLE DE LÂMPADA INTELIGENTE TUYA - v0.2

1. Controlar Lâmpada
2. Gerenciar Dispositivos
0. Sair
```

### Adicionar Novos Dispositivos

**Opção 1: Wizard Automático (Recomendado)**

1. Menu Inicial → `2. Gerenciar Dispositivos`
2. Menu Admin → `1. Executar Wizard`
3. Siga as instruções na tela

O wizard vai:
- Procurar dispositivos na rede
- Pedir chaves de acesso local
- Atualizar os arquivos automaticamente

**Opção 2: Adicionar Manualmente**

1. Menu Admin → `3. Adicionar Dispositivo`
2. Preencha as informações:
   - Nome do dispositivo
   - ID (Tuya Device ID)
   - Chave de acesso local (Key)
   - IP (opcional, pode deixar em branco)
   - MAC, UUID, Modelo (opcionais)

### Localizar Informações do Dispositivo

#### ID e Key (Obrigatórios)

**Via App Tuya:**
1. Abra o app Tuya
2. Selecione o dispositivo
3. Vá para Configurações/Info do Dispositivo
4. Procure por "ID" e "Local Key"

**Via Tuya IoT Console:**
1. Acesse https://iot.tuya.com
2. Vá para Cloud → Devices
3. Encontre seu dispositivo
4. Procure os dados de autenticação

#### IP do Dispositivo

**Via Roteador/WiFi:**
1. Acesse o painel do seu roteador
2. Procure por "Dispositivos Conectados" ou "Connected Devices"
3. Localize o dispositivo Tuya pela MAC
4. Copie o IP

**Via Tinytuya Wizard:**
1. Execute o wizard
2. Os IPs são descobertos automaticamente

### Estrutura de Arquivos

```
v0.2/
├── main.py                 # Arquivo principal
├── device_manager.py       # Gerenciador de dispositivos
├── devices.json           # Dispositivos (formato customizado)
├── tinytuya.json          # Saída do wizard do tinytuya
├── tuya-raw.json          # Dados raw do wizard
└── backup_YYYYMMDD_HHMMSS/ # Backups automáticos
```

#### devices.json (Formato)

```json
[
    {
        "id": "ebecbc6d2743ca812dzudh",
        "name": "Quarto Frente",
        "key": "SJ*:Nn{{+VN2kH3^",
        "ip": "192.168.1.6",
        "mac": "18:de:50:05:6b:e1",
        "uuid": "66d3673805254b5e",
        "model": "10W"
    }
]
```

## 🔧 Operações Comuns

### Descobrir Novos Dispositivos
```
Menu Admin → 1. Executar Wizard
```

### Ver Status de Conectividade
```
Menu Controle → Selecionar Lâmpada
(Mostra 🟢 Online ou 🔴 Offline)
```

### Configurar IP de um Dispositivo
```
Menu Admin → 4. Editar Dispositivo
Selecione o dispositivo
Digite o novo IP
```

### Fazer Backup
```
Menu Admin → 8. Fazer Backup
(Cria pasta backup_YYYYMMDD_HHMMSS)
```

### Exportar Lista de Dispositivos
```
Menu Admin → 6. Exportar Dispositivos
Digite o nome do arquivo (ou deixe em branco)
```

### Importar de Outro Arquivo
```
Menu Admin → 7. Importar Dispositivos
Digite o caminho do arquivo
```

## ⚙️ Configuração Recomendada

1. **Execute o Wizard primeiro** para descobrir todos os dispositivos
2. **Anote os IPs** dos dispositivos mais usados
3. **Configure os IPs** via Menu Admin → Editar
4. **Faça um Backup** via Menu Admin → Backup
5. **Exporte a lista** via Menu Admin → Exportar

## 🐛 Solução de Problemas

### "Arquivo devices.json não encontrado"
- Execute o Wizard para criar
- Ou adicione manualmente dispositivos

### Lâmpada mostra "Offline" mas está ligada
- Verifique se está na mesma rede
- Configure o IP correto no dispositivo
- Tente reconectar via app Tuya

### Timeout na conexão
- Aumentar timeout em `device_manager.py` (padrão: 5s)
- Verificar conexão WiFi do dispositivo
- Usar IP em vez de "scan"

### Wizard não encontra dispositivos
- Certifique-se de estar na mesma rede WiFi
- Dispositivos devem estar online
- Tente resetar o dispositivo Tuya

## 📝 Notas

- Backups são criados automaticamente antes do wizard
- Dispositivos duplicados são evitados automáticamente
- Imports apenas adicionam novos dispositivos
- Edições salvam automaticamente

## 🔐 Segurança

- **Nunca** compartilhe suas chaves de acesso local (key)
- **Nunca** publique suas IPs na internet
- Mantenha os arquivos JSON em local seguro
- Backups contêm dados sensíveis - proteja!

---

**Desenvolvido para a disciplina de Tópicos Avançados de Programação**
