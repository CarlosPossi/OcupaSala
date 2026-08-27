import os
import sys

# Adiciona o diretório src ao path para permitir imports relativos quando executado de fora
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.utils import RESERVAS_FILE, load_json, save_json

# =========================
# CASOS DE USO
# =========================

def visualizar_salas():
    print("\n📌 Salas disponíveis:")
    print("- Sala 1")
    print("- Sala 2")
    print("- Sala 3")


def listar_reservas(reservas):
    print("\n📋 Reservas:")
    if not reservas:
        print("Nenhuma reserva encontrada.")
        return

    for r in reservas:
        # Nota: O formato JSON do app.py tem campos diferentes (dia, inicio, fim)
        # Adaptando para mostrar informações extras se disponíveis
        horario = f"{r.get('dia', '')} {r.get('inicio', '')}-{r.get('fim', '')}".strip()
        if not horario: horario = r.get('horario', 'N/A')
        
        print(f"Nome: {r['nome']} | Sala: {r['sala']} | Horário: {horario}")


def validar_disponibilidade(reservas, sala, horario):
    # Nota: Esta validação simples do CLI original não lida com o formato novo de dia/inicio/fim
    # Para manter compatibilidade simples, verificamos apenas igualdade exata se 'horario' for usado
    for r in reservas:
        if r["sala"] == sala and r.get("horario") == horario:
            return False
    return True


def reservar_sala(reservas):
    print("\n📝 Nova Reserva (Modo CLI)")

    nome = input("Digite seu nome: ").strip()
    sala = input("Digite a sala: ").strip()
    horario = input("Digite o horário (ex: 2026-05-10 10:00-11:00): ").strip()

    # validação de entrada
    if not nome or not sala or not horario:
        print("❌ Dados inválidos!")
        return

    # valida disponibilidade
    if not validar_disponibilidade(reservas, sala, horario):
        print("❌ Sala já reservada nesse horário!")
        return

    reservas.append({
        "nome": nome,
        "sala": sala,
        "horario": horario
    })

    save_json(RESERVAS_FILE, reservas)
    print("✅ Reserva realizada com sucesso!")


def cancelar_reserva(reservas):
    print("\n❌ Cancelar Reserva")

    nome = input("Digite seu nome: ").strip()

    encontrado = False
    for r in list(reservas):
        if r["nome"] == nome:
            reservas.remove(r)
            encontrado = True
    
    if encontrado:
        save_json(RESERVAS_FILE, reservas)
        print("✅ Reserva(s) cancelada(s)!")
    else:
        print("❌ Nenhuma reserva encontrada para esse nome.")


# =========================
# MENU
# =========================

def menu():
    while True:
        # Recarregar reservas a cada loop para pegar mudanças do Web App
        reservas = load_json(RESERVAS_FILE)
        
        print("\n=== Sistema de Reserva de Salas (CLI) ===")
        print("1 - Visualizar salas")
        print("2 - Listar reservas")
        print("3 - Reservar sala")
        print("4 - Cancelar reserva")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            visualizar_salas()
        elif opcao == "2":
            listar_reservas(reservas)
        elif opcao == "3":
            reservar_sala(reservas)
        elif opcao == "4":
            cancelar_reserva(reservas)
        elif opcao == "0":
            print("Encerrando sistema...")
            break
        else:
            print("❌ Opção inválida!")


if __name__ == "__main__":
    menu()
