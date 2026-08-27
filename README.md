# 🏫 FIAP Room Reservation System

![thumbnail](docs/image.png)

## 📌 Descrição do Problema
A dificuldade de encontrar salas disponíveis para estudo e a falta de uma organização centralizada para reservas geram conflitos e desperdício de tempo para alunos e funcionários da FIAP. O sistema manual ou a falta dele torna o processo ineficiente.

## 💡 Solução Proposta
Desenvolvemos uma aplicação web intuitiva utilizando **Python e Flask** que centraliza a gestão de salas. O sistema permite que usuários se cadastrem, realizem login e gerenciem suas reservas de forma autônoma. Um dashboard interativo fornece uma visão clara da ocupação das salas em tempo real, otimizando o uso dos espaços físicos da instituição.

## 🚀 Evoluções do Checkpoint 1 para o Checkpoint 2
* **Interface:** Transição de uma aplicação via terminal (CLI) para uma interface Web moderna e responsiva.
* **Arquitetura:** Reestruturação do código seguindo o padrão modular com **Blueprints**, separando rotas de autenticação, lógica de visualização e modelos.
* **Funcionalidades:** Inclusão de um sistema de **Autenticação (Login/Cadastro)** com hash de senha para segurança.
* **Persistência:** Melhoria na organização dos dados em arquivos JSON estruturados.
* **Visualização:** Implementação de um **Dashboard de Ocupação** com estatísticas e filtros de data/horário.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** [Python 3.10+](https://www.python.org/)
* **Framework Web:** [Flask](https://flask.palletsprojects.com/)
* **Template Engine:** [Jinja2](https://jinja.palletsprojects.com/)
* **Segurança:** [Werkzeug](https://werkzeug.palletsprojects.com/) (Password Hashing)
* **Persistência de Dados:** JSON
* **Servidor WSGI:** [Gunicorn](https://gunicorn.org/) (para deploy)

## ▶️ Como Executar

### 📋 Pré-requisitos
* Python 3.10 ou superior instalado.
* `pip` (gerenciador de pacotes do Python).

### 🔧 Instalação
1. Clone o repositório ou baixe os arquivos.
2. Navegue até a pasta do projeto.
3. Instale as dependências:
   ```bash
   pip install -r src/requirements.txt
   ```

### 🚀 Execução
Para iniciar o servidor de desenvolvimento:
```bash
python src/app.py
```
O sistema estará disponível em `http://localhost:5000`.

## 📁 Estrutura do Projeto
* `src/app.py`: Ponto de entrada da aplicação e configuração do servidor.
* `src/auth/`: Módulo responsável pela autenticação (rotas de login e cadastro).
* `src/views/`: Módulo principal contendo a lógica de reservas, dashboard e relatórios.
* `src/models/`: Definição das classes de dados (Usuário, Reserva, Sala) e utilitários de persistência.
* `src/data/`: Armazenamento dos arquivos JSON (`users.json`, `reservas.json`).
* `src/templates/`: Arquivos HTML da interface.
* `src/static/`: Arquivos estáticos como CSS e imagens da UI.

## 📋 Funcionalidades Implementadas

### Cadastro e Login
* **Cadastro:** Permite novos usuários criarem contas com validação básica.
* **Login:** Acesso restrito via e-mail e senha, com sessões seguras.

### Casos de Uso
| Caso de Uso | Status |
| :--- | :--- |
| Criar conta de usuário | ✅ Implementado |
| Autenticar usuário (Login/Logout) | ✅ Implementado |
| Visualizar disponibilidade de salas no Dashboard | ✅ Implementado |
| Realizar reserva de sala | ✅ Implementado |
| Validar conflitos de horário em reservas | ✅ Implementado |
| Listar minhas reservas e todas as reservas | ✅ Implementado |
| Cancelar reserva própria | ✅ Implementado |
| Gerar relatórios de ocupação | ⚠️ Parcial |

## 🌟 Diferencial do Projeto

### Descrição
O grande diferencial é o **Dashboard de Ocupação Inteligente**. Ele não apenas lista reservas, mas calcula em tempo real a porcentagem de ocupação de cada sala baseada no dia atual e destaca quais salas estão ocupadas "Agora".

### Justificativa
Em ambientes acadêmicos dinâmicos, a visualização rápida e gráfica da disponibilidade é mais eficiente do que ler tabelas de horários. Isso permite uma tomada de decisão imediata pelo aluno que busca um local para estudar.

### Referências
* [Documentação Flask](https://flask.palletsprojects.com/en/3.0.x/)
* [Jinja2 Documentation](https://jinja.palletsprojects.com/en/3.1.x/)
* [FIAP - Material de Microservices and Web Applications](https://www.fiap.com.br/)

## 🎥 Demonstração
![Demo do sistema](docs/animacao.gif)
*Veja o funcionamento básico do sistema no GIF acima.*

## 👥 Integrantes do Grupo
* **Fabio Henrique Santos Farias** (RM: 552453)
* **Carlos Augusto da Cruz Possi** (RM: 558758)
* **João Pedro Bernardo Santos da Silva** (RM: 557142)

## 🔗 Links
🧠 **Miro (Documentação e Diagramas):** [Acessar Board](https://miro.com/app/board/uXjVGwGD7H4=/?share_link_id=899993910065)  
💻 **Google Colab (Protótipo Inicial):** [Acessar Notebook](https://colab.research.google.com/drive/1IDkm92TqKFn3YvFlW22JfamUdzKsnMz9?usp=sharing)  
📺 **Render:** [Link do deploy](https://fiap-room-reservation-system.onrender.com/)  
