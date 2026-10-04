# 🏢 OcupaSala

Sistema web de reserva de espaços físicos para qualquer organização — escola, faculdade, escritório, coworking, biblioteca. Um único painel para ver o que está livre agora, reservar sem conflito e acompanhar o uso dos espaços.

> **Versão atual:** protótipo funcional (Python + Flask) com persistência em arquivos JSON e dados de demonstração.
> <br>
> Os fluxos — cadastro, login, busca, reserva, recorrência, cancelamento, relatórios — funcionam de verdade.

---

## ✨ O que diferencia o OcupaSala

| Recurso | Para que serve |
| :--- | :--- |
| **Sugestões inteligentes em conflito** | Ao tentar reservar um horário ocupado, o sistema propõe os horários livres mais próximos no mesmo espaço e outros espaços livres que comportam o grupo — a um clique de distância. |
| **Buscar espaço livre** | Informe dia, horário e nº de pessoas: só aparecem espaços realmente livres, ordenados pelo melhor encaixe de capacidade (não se gasta um auditório para 4 pessoas). |
| **Agenda do dia em linha do tempo** | Visão por espaço de 07h às 22h, com marcador de "agora", reservas suas destacadas e atalho para reservar um horário vago. |
| **Reservas recorrentes** | Repita uma reserva por 2, 4, 8 ou 12 semanas; o sistema valida conflito em todas as datas e permite cancelar "só esta" ou "esta e as seguintes". |
| **Validação de lotação** | O nº de participantes é checado contra a capacidade do espaço. |
| **Exportar para a sua agenda (.ics)** | Leve suas próximas reservas para Google Agenda, Outlook ou Apple Calendar. |
| **Status em tempo real** | O dashboard mostra, por espaço, "Ocupada até 10:00 · Fulano" ou "Livre até 14:00", com atalho para reservar. |
| **Relatórios reais** | Total, semana, horário de pico, horas por espaço e por unidade, ranking de uso e espaços ociosos — calculados das reservas verdadeiras. |
| **Catálogo multiorganização** | `tipo` + `unit` permitem que escola, faculdade e escritório convivam no mesmo sistema; qualquer usuário cadastra novos espaços pela interface. |

---

## ▶️ Como rodar

### Pré-requisitos
* Python 3.10 ou superior (`python --version`)
* `pip`

### Passo a passo
1. Entre na pasta do projeto:
   ```bash
   cd OcupaSala
   ```
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   ```
   * **Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```
   * **Windows PowerShell:**
     ```powershell
     venv\Scripts\Activate.ps1
     ```
   * **Windows CMD:**
     ```cmd
     venv\Scripts\activate.bat
     ```
3. Instale as dependências:
   ```bash
   pip install -r src/requirements.txt
   ```
4. Inicie o servidor:
   ```bash
   python src/app.py
   ```
5. Abra no navegador:
   `http://localhost:5000`
   
---

## ⚙️ Variáveis de ambiente
*Todas são opcionais.*

| Variável | Padrão | Função |
| :--- | :--- | :--- |
| `PORT` | `5000` | Porta |
| `SECRET_KEY` | Gerada e salva em `src/data/.secret_key` | Chave de assinatura das sessões |
| `OCUPASALA_TZ` | `America/Sao_Paulo` | Fuso usado para "hoje" e "agora" |
| `OCUPASALA_DATA_DIR` | `src/data` | Pasta onde os JSON são gravados |
| `FLASK_DEBUG` | `0` | `1` ativa o modo de desenvolvimento |

---

## 🧱 Tecnologias

* Python 3.10+
* Flask
* Jinja2
* Werkzeug (hash de senha)
* Gunicorn
* HTML/CSS próprios (Inter + Sora)
* Persistência em JSON (gravação atômica)

---

## 📁 Estrutura

```text
OcupaSala/
├── README.md
├── Procfile
├── .gitignore
├── docs/
│   ├── demo-ocupasala.mp4
│   ├── REQUISITOS.md
│   ├── DIAGRAMAS.md
│   └── ROTEIROS_VIDEO.md
└── src/
    ├── app.py
    ├── requirements.txt
    ├── auth/
    │   └── routes.py
    ├── views/
    │   └── routes.py
    ├── models/
    │   ├── entidades.py
    │   ├── servicos.py
    │   ├── seed.py
    │   └── utils.py
    ├── templates/
    ├── static/
    └── data/
```

---

## 🗺️ Rotas principais

| Rota | Descrição |
| :--- | :--- |
| `/login`, `/cadastro`, `/logout` | Autenticação |
| `/dashboard` | Visão geral e status em tempo real |
| `/disponibilidade` | Buscar espaço livre |
| `/agenda?dia=AAAA-MM-DD` | Linha do tempo do dia |
| `/reservar` | Nova reserva |
| `/reservas?visao=proximas\|minhas\|concluidas\|todas` | Quadro de reservas |
| `/reservas/exportar.ics` | Exporta suas próximas reservas |
| `/espacos` | Catálogo de espaços |
| `/relatorios`, `/configuracoes` | Métricas e perfil/senha |

> **Nota:** A rota `/reservar` aceita `/reservar?sala=&dia=&inicio=&fim=` para pré-preencher os dados da reserva.

---

## ⚠️ Limitações conhecidas

* **Persistência em JSON:** Adequada para demo e uso leve; para produção, migrar para banco de dados (ex.: PostgreSQL).
* **Perfis de usuário:** Todos os usuários têm o mesmo papel — não há perfil de administrador por unidade.
* **Proteção CSRF:** Sem proteção CSRF.
* **E-mails/notificações:** Sem envio real de e-mails ou notificações.
* **Servidor:** O servidor de desenvolvimento do Flask não deve ser usado em produção — use o Gunicorn (`Procfile`).

---

## 👥 Autores

* Fabio Henrique Santos Farias
* Carlos Augusto da Cruz Possi
* João Pedro Bernardo Santos da Silva
