# 🏫 FIAP Room Reservation System


## 📌 Descrição do Problema
A dificuldade de encontrar salas disponíveis para estudo e a falta de uma organização centralizada para reservas geram conflitos e desperdício de tempo para alunos e funcionários da FIAP. O sistema manual ou a falta dele torna o processo ineficiente.

## 💡 Solução Proposta
Desenvolvemos uma aplicação web intuitiva utilizando **Python e Flask** que centraliza a gestão de salas. O sistema permite que usuários se cadastrem, realizem login e gerenciem suas reservas de forma autônoma. Um dashboard interativo fornece uma visão clara da ocupação das salas em tempo real, otimizando o uso dos espaços físicos da instituição.

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

## 🌟 Diferencial do Projeto

### Descrição
O grande diferencial é o **Dashboard de Ocupação Inteligente**. Ele não apenas lista reservas, mas calcula em tempo real a porcentagem de ocupação de cada sala baseada no dia atual e destaca quais salas estão ocupadas "Agora".

### Justificativa
Em ambientes acadêmicos dinâmicos, a visualização rápida e gráfica da disponibilidade é mais eficiente do que ler tabelas de horários. Isso permite uma tomada de decisão imediata pelo aluno que busca um local para estudar.

## 👥 Integrantes do Grupo
* **Fabio Henrique Santos Farias** (RM: 552453)
* **Carlos Augusto da Cruz Possi** (RM: 558758)
* **João Pedro Bernardo Santos da Silva** (RM: 557142)

## 🔗 Links
🧠 **Miro (Documentação e Diagramas):** [Acessar Board](https://miro.com/app/board/uXjVHsCVu7Q=/)  
🧠 **Trello (Tarefas):** [Acessar Tarefas](https://trello.com/invite/b/6a8f911f7186e4e292d7e506/ATTIfa996809f947fda12cfdca5966903b0f232992B6/checkpoint-4)


