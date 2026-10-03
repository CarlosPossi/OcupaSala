"""Utilitários de persistência (JSON em disco) e configuração básica."""
import json
import os
import secrets
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("OCUPASALA_DATA_DIR", os.path.join(BASE_DIR, "data"))
USERS_FILE = os.path.join(DATA_DIR, "users.json")
RESERVAS_FILE = os.path.join(DATA_DIR, "reservas.json")
SALAS_FILE = os.path.join(DATA_DIR, "salas.json")
SECRET_FILE = os.path.join(DATA_DIR, ".secret_key")

# Fuso usado para "agora" / "hoje". Pode ser trocado via variável de ambiente.
TZ = ZoneInfo(os.environ.get("OCUPASALA_TZ", "America/Sao_Paulo"))

os.makedirs(DATA_DIR, exist_ok=True)


def agora():
    return datetime.now(TZ)


def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def save_json(filepath, data):
    """Grava de forma atômica (arquivo temporário + rename) para não corromper o JSON."""
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, filepath)


def get_secret_key():
    """Chave de sessão: variável SECRET_KEY, ou uma chave aleatória persistida em data/."""
    env = os.environ.get("SECRET_KEY")
    if env:
        return env
    try:
        with open(SECRET_FILE, "r") as f:
            return f.read().strip()
    except OSError:
        key = secrets.token_hex(32)
        with open(SECRET_FILE, "w") as f:
            f.write(key)
        return key
