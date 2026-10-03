"""Dados de demonstração. As datas são relativas a HOJE, então a demo nunca fica 'velha'."""
from datetime import timedelta
from models.entidades import Usuario, Reserva, SEED_SALAS
from models.utils import USERS_FILE, RESERVAS_FILE, SALAS_FILE, load_json, save_json, agora

DEMO_SENHA = "123456"
DEMO_USUARIOS = [
    ("Mariana Souza", "mariana.souza@faculdade-demo.com", "Coordenação · Faculdade"),
    ("Rafael Lima", "rafael.lima@empresa-demo.com", "Colaborador · Escritório"),
    ("Ana Torres", "ana.torres@escola-demo.com", "Aluna · Escola"),
]


def semear_demo(forcar=False):
    """Cria usuários/espaços/reservas de exemplo se o sistema está vazio (ou se forcar=True)."""
    if not forcar and load_json(USERS_FILE):
        return False
    hoje = agora().date()
    d = lambda n: (hoje + timedelta(days=n)).strftime("%Y-%m-%d")
    save_json(SALAS_FILE, [s.to_dict() for s in SEED_SALAS])
    save_json(USERS_FILE, [Usuario(n, e, DEMO_SENHA).to_dict() for n, e, _ in DEMO_USUARIOS])
    mari, rafa, ana = (u[:2] for u in DEMO_USUARIOS)

    def r(sala, dia, ini, fim, quem, titulo, pessoas):
        return Reserva(sala, d(dia), ini, fim, quem[1], quem[0], titulo, pessoas).to_dict()

    reservas = [
        r("Sala de Aula 12", 0, "08:00", "10:00", mari, "Aula de Algoritmos", 30),
        r("Sala de Reunião A", 0, "09:00", "10:30", rafa, "Alinhamento semanal", 6),
        r("Sala de Reunião A", 0, "14:00", "15:00", rafa, "Revisão de proposta", 5),
        r("Sala de Estudos 3", 0, "16:00", "18:00", ana, "Grupo de estudo – Física", 5),
        r("Laboratório de Informática", 0, "13:00", "17:00", mari, "Oficina de Python", 20),
        r("Estação Coworking 5", 1, "09:00", "12:00", rafa, "Foco: relatório trimestral", 1),
        r("Laboratório de Informática", 1, "13:00", "15:00", mari, "Monitoria", 18),
        r("Auditório Principal", 2, "10:00", "12:00", ana, "Feira de Ciências", 90),
        r("Sala de Reunião B", 2, "15:00", "16:00", rafa, "Entrevista de candidato", 3),
        r("Sala de Aula 12", 3, "19:00", "21:00", mari, "Workshop de UX", 28),
    ]
    save_json(RESERVAS_FILE, reservas)
    return True
