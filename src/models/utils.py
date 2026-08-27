import os
import json

# Caminhos dos arquivos de dados
# O BASE_DIR agora é resolvido a partir de models/utils.py
# Subindo um nível (..) para chegar em src/ e depois em data/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
RESERVAS_FILE = os.path.join(DATA_DIR, "reservas.json")

# Garante que a pasta data exista
os.makedirs(DATA_DIR, exist_ok=True)

# Inicializa arquivos se não existirem
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump([], f)
if not os.path.exists(RESERVAS_FILE):
    with open(RESERVAS_FILE, 'w') as f:
        json.dump([], f)

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
