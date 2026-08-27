from werkzeug.security import generate_password_hash, check_password_hash


class Usuario:
    """Representa uma pessoa cadastrada no OcupaSala (aluno ou funcionário)."""

    def __init__(self, nome, email, senha=None, senha_hash=None):
        self.nome = nome
        self.email = email
        if senha:
            self.senha_hash = generate_password_hash(senha)
        else:
            self.senha_hash = senha_hash

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha_hash
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            nome=data.get("nome"),
            email=data.get("email"),
            senha_hash=data.get("senha")
        )


class Sala:
    """Representa uma sala reservável do campus (Diagrama de Classes: Sala)."""

    def __init__(self, nome, capacidade=None):
        self.nome = nome
        self.capacidade = capacidade

    def to_dict(self):
        return {
            "nome": self.nome,
            "capacidade": self.capacidade
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            nome=data.get("nome"),
            capacidade=data.get("capacidade")
        )

    def __repr__(self):
        return f"Sala({self.nome}, capacidade={self.capacidade})"


class Reserva:
    """Representa a reserva de uma Sala feita por um Usuario em um dia/horário."""

    def __init__(self, sala, dia, inicio, fim, email, nome=None):
        self.sala = sala
        self.dia = dia
        self.inicio = inicio
        self.fim = fim
        self.email = email
        self.nome = nome

    def to_dict(self):
        return {
            "sala": self.sala,
            "dia": self.dia,
            "inicio": self.inicio,
            "fim": self.fim,
            "email": self.email,
            "nome": self.nome
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            sala=data.get("sala"),
            dia=data.get("dia"),
            inicio=data.get("inicio"),
            fim=data.get("fim"),
            email=data.get("email"),
            nome=data.get("nome")
        )


# Catálogo de salas disponíveis no campus (relação Sala "1" -- "0..*" Reserva).
# Centralizar aqui evita strings soltas ("Sala 1", "Sala 2"...) espalhadas pelas rotas
# e passa a ser a fonte única de verdade para nome/capacidade de cada sala.
CATALOGO_SALAS = [
    Sala(nome="Sala 1", capacidade=4),
    Sala(nome="Sala 2", capacidade=6),
    Sala(nome="Sala 3", capacidade=10),
]


def get_sala_by_nome(nome):
    """Retorna o objeto Sala correspondente ao nome, ou None se não existir no catálogo."""
    return next((s for s in CATALOGO_SALAS if s.nome == nome), None)
