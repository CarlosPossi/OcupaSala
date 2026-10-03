"""Classes de domínio: Usuario, Sala e Reserva + catálogo de espaços."""
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from models.utils import SALAS_FILE, load_json, save_json


class Usuario:
    """Pessoa cadastrada (estudante, colaborador, visitante...)."""

    def __init__(self, nome, email, senha=None, senha_hash=None):
        self.nome = nome
        self.email = email
        self.senha_hash = generate_password_hash(senha) if senha else senha_hash

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {"nome": self.nome, "email": self.email, "senha": self.senha_hash}

    @classmethod
    def from_dict(cls, data):
        return cls(nome=data.get("nome"), email=data.get("email"), senha_hash=data.get("senha"))


class Sala:
    """Espaço reservável. `tipo` = natureza do espaço; `unidade` = organização a que pertence."""

    def __init__(self, nome, capacidade=None, tipo="Sala", unidade="Geral"):
        self.nome = nome
        self.capacidade = capacidade
        self.tipo = tipo
        self.unidade = unidade

    @property
    def unidade_slug(self):
        mapa = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
        return (self.unidade or "geral").lower().translate(mapa)

    def to_dict(self):
        return {"nome": self.nome, "capacidade": self.capacidade, "tipo": self.tipo, "unidade": self.unidade}

    @classmethod
    def from_dict(cls, data):
        return cls(nome=data.get("nome"), capacidade=data.get("capacidade"),
                   tipo=data.get("tipo", "Sala"), unidade=data.get("unidade", "Geral"))


class Reserva:
    """Reserva de uma Sala por um Usuario em um dia/horário."""

    def __init__(self, sala, dia, inicio, fim, email, nome=None, titulo="", participantes=1,
                 serie_id=None, id=None, criada_em=None):
        self.id = id or uuid.uuid4().hex[:10]
        self.sala = sala
        self.dia = dia
        self.inicio = inicio
        self.fim = fim
        self.email = email
        self.nome = nome
        self.titulo = titulo
        self.participantes = participantes
        self.serie_id = serie_id
        self.criada_em = criada_em

    def to_dict(self):
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: data.get(k) for k in
                      ("sala", "dia", "inicio", "fim", "email", "nome", "titulo",
                       "participantes", "serie_id", "id", "criada_em")})


# ---------- Catálogo de espaços ----------
SEED_SALAS = [
    Sala("Sala de Aula 12", 35, "Sala de Aula", "Faculdade"),
    Sala("Laboratório de Informática", 25, "Laboratório", "Faculdade"),
    Sala("Sala de Estudos 3", 6, "Sala de Estudo", "Escola"),
    Sala("Auditório Principal", 120, "Auditório", "Escola"),
    Sala("Sala de Reunião A", 8, "Sala de Reunião", "Escritório"),
    Sala("Sala de Reunião B", 4, "Sala de Reunião", "Escritório"),
    Sala("Estação Coworking 5", 1, "Estação de Trabalho", "Escritório"),
]


def listar_salas():
    dados = load_json(SALAS_FILE)
    if not dados:
        save_json(SALAS_FILE, [s.to_dict() for s in SEED_SALAS])
        return list(SEED_SALAS)
    return [Sala.from_dict(d) for d in dados]


def get_sala_by_nome(nome):
    return next((s for s in listar_salas() if s.nome == nome), None)


def criar_sala(nome, tipo, unidade, capacidade):
    nome = (nome or "").strip()
    tipo = (tipo or "").strip() or "Sala"
    unidade = (unidade or "").strip() or "Geral"
    if not nome:
        return False, "Dê um nome ao espaço antes de salvar."
    salas = listar_salas()
    if any(s.nome.lower() == nome.lower() for s in salas):
        return False, f'Já existe um espaço chamado "{nome}".'
    try:
        cap = int(capacidade)
        if cap <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return False, "Informe uma capacidade válida (inteiro maior que zero)."
    salas.append(Sala(nome, cap, tipo, unidade))
    save_json(SALAS_FILE, [s.to_dict() for s in salas])
    return True, f'Espaço "{nome}" criado com sucesso.'


def remover_sala(nome, reservas_existentes):
    if any(r.get("sala") == nome for r in reservas_existentes):
        return False, "Esse espaço tem reservas e não pode ser excluído."
    salas = listar_salas()
    restantes = [s for s in salas if s.nome != nome]
    if len(restantes) == len(salas):
        return False, "Esse espaço não foi encontrado."
    save_json(SALAS_FILE, [s.to_dict() for s in restantes])
    return True, f'Espaço "{nome}" removido.'
