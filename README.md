# Serial CLI

Uma ferramenta de linha de comando para comunicação serial interativa, desenvolvida em Python. O Serial CLI permite estabelecer uma sessão de comunicação bidirecional com dispositivos conectados via porta serial.

## Funcionalidades

- ✨ **Shell interativo**: Interface de linha de comando intuitiva para comunicação serial
- 🔧 **Configuração flexível**: Baudrate, porta serial e timeout personalizáveis
- 🎨 **Interface rica**: Utiliza Rich para uma experiência visual aprimorada
- 📊 **Monitoramento de dados**: Exibe estatísticas de bytes enviados/recebidos
- 🔍 **Highlighting**: Destaque automático de valores hexadecimais nas respostas
- 💻 **Comandos do sistema**: Execute comandos do terminal com `!comando`
- 📜 **Execução de scripts**: Execute comandos em lote a partir de arquivos
- 👁️ **Modo de monitoramento**: Visualize dados da porta serial em tempo real

## Instalação

### Pré-requisitos
- Python 3.10 ou superior

### Instalação via pip

```bash
pip install .
```

### Instalação para desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/commonProgrammer/serial-cli.git
cd serial-cli

# Instale as dependências
pip install -e .
```

## Como usar

### Comando básico

Execute o Serial CLI com as configurações padrão:

```bash
serial-cli start
```

### Configuração de parâmetros

```bash
serial-cli start --port /dev/ttyUSB0 --baudrate 115200 --timeout 10
```

### Executar como módulo Python

```bash
python -m serial_cli start
```

### Monitoramento simples

Para apenas monitorar dados da porta serial:

```bash
serial-cli connect --port /dev/ttyUSB0 --baudrate 115200
```

## Parâmetros de configuração

| Parâmetro | Opção curta | Padrão | Descrição |
|-----------|-------------|--------|-----------|
| `--port` | `-p` | `/dev/ttyUSB0` (Linux/macOS)<br>`COM3` (Windows) | Porta serial a ser utilizada |
| `--baudrate` | `-b` | `9600` | Taxa de transmissão (baud rate) |
| `--timeout` | | `5` | Timeout para comunicação serial (segundos) |

## Usando o shell interativo

Após iniciar o Serial CLI, você entrará em um shell interativo onde pode:

### Enviar comandos seriais
Use o comando `send` para enviar dados via serial:
```
/dev/ttyUSB0> send AT
/dev/ttyUSB0> 
```

Para enviar e aguardar resposta automaticamente:
```
/dev/ttyUSB0> send --wait AT+GMR
ESP32-C3 (revision 3)
```

### Executar comandos do sistema
Use `!` como prefixo para executar comandos do sistema operacional:
```
/dev/ttyUSB0> !ls -la
total 24
drwxr-xr-x  3 user user 4096 Sep 11 10:30 .
...
```

### Comandos especiais
- `send <dados>` - Enviar dados via serial
- `send --wait <dados>` - Enviar dados e aguardar resposta
- `read <bytes>` - Ler número específico de bytes
- `read <terminator>` - Ler até encontrar terminador
- `exit` - Sair do shell
- `clear` - Limpar a tela

### Executar comandos de arquivos

O comando `start` também permite executar comandos de arquivos:

```bash
# Executar comandos de um arquivo
serial-cli start comandos.txt 

# Ou múltiplos arquivos
serial-cli start comandos1.txt comandos2.txt
```

#### Exemplo de arquivo de comandos

Você pode criar um arquivo de texto (por exemplo, `comandos.txt`) com uma sequência de comandos para serem enviados ao dispositivo serial. No Serial CLI, o prefixo `!` executa comandos do sistema, e a sintaxe `!(comando)` é equivalente ao uso de `$()` no bash, ou seja, executa o comando e insere sua saída.

Exemplo de conteúdo para `comandos.txt`:

```bash
send Olá, dispositivo! # envia o texto diretamente pela serial.
!ls /dev/ttyUSB* # executa o comando no sistema e mostra a saída.
!echo Teste direto do sistema # executa outro comando do sistema.
send !(date) # executa o comando `date` no sistema e envia o resultado pela serial.
```

### Recursos visuais
- **Valores hexadecimais** são destacados em amarelo (ex: `0x41`, `0xFF`)
- **Estatísticas** de transmissão são exibidas em ciano
- **Erros** são mostrados em vermelho
- **Prompt** colorido indica a porta conectada

## Exemplos de uso

### Comunicação com Arduino
```bash
serial-cli start --port /dev/ttyACM0 --baudrate 9600
```

### Comunicação com módulo ESP32
```bash
serial-cli start --port /dev/ttyUSB0 --baudrate 115200
```

### Windows com dispositivo USB
```bash
serial-cli start --port COM4 --baudrate 57600
```

## Tratamento de erros

O Serial CLI trata automaticamente os seguintes cenários:
- **Porta serial não encontrada**: Exibe mensagem de erro clara
- **Timeout de comunicação**: Indica quando não há resposta do dispositivo
- **Comandos inválidos**: Diferencia entre comandos do sistema e dados seriais
- **Interrupção por teclado**: Permite sair graciosamente com Ctrl+C

## Dependências

- **prompt-toolkit**: Interface interativa aprimorada
- **click**: Interface de linha de comando
- **pyserial**: Comunicação serial
- **rich**: Interface rica no terminal
- **rich-click**: Integração entre Rich e Click

## Desenvolvimento

### Estrutura do projeto

```
serial_cli/
├── __init__.py
├── __main__.py          # Ponto de entrada como módulo
├── cli.py               # Interface de linha de comando
└── core.py              # Lógica principal do Serial CLI
```

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## Autor

**André Escorel** - [gustavo.escorel@gmail.com](mailto:gustavo.escorel@gmail.com)

## Links

- [Repositório no GitHub](https://github.com/commonProgrammer/serial-cli)
- [Homepage do projeto](https://github.com/commonProgrammer/serial-cli)