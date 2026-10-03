"""Regras de negócio: conflitos, sugestões inteligentes, status, relatórios e exportação .ics."""
from datetime import datetime, timedelta
from models.utils import RESERVAS_FILE, load_json, save_json, agora

ABERTURA = "07:00"
FECHAMENTO = "22:00"
JANELA_HORAS = 15  # 07h–22h: base do cálculo de % de ocupação


def hm(texto):
    """'09:30' -> minutos desde 00:00."""
    h, m = texto.split(":")
    return int(h) * 60 + int(m)


def fmt(minutos):
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def carregar_reservas():
    """Lê as reservas, completando campos novos em registros antigos (migração suave)."""
    dados = load_json(RESERVAS_FILE)
    alterou = False
    for r in dados:
        if not r.get("id"):
            r["id"] = f"{abs(hash((r.get('sala'), r.get('dia'), r.get('inicio'), r.get('email')))) % 10**10:010d}"
            alterou = True
        r.setdefault("titulo", "")
        r.setdefault("participantes", 1)
        r.setdefault("serie_id", None)
    if alterou:
        save_json(RESERVAS_FILE, dados)
    return dados


def conflita(reservas, sala, dia, inicio, fim):
    """Retorna a reserva que conflita (ou None)."""
    for r in reservas:
        if r["sala"] == sala and r["dia"] == dia and inicio < r["fim"] and fim > r["inicio"]:
            return r
    return None


def validar_periodo(dia, inicio, fim):
    """Valida data/horários. Retorna mensagem de erro ou None."""
    try:
        data = datetime.strptime(dia, "%Y-%m-%d").date()
        hm(inicio), hm(fim)
    except (TypeError, ValueError, AttributeError):
        return "Data ou horário inválido."
    if inicio >= fim:
        return "O horário de término precisa ser depois do início."
    if inicio < ABERTURA or fim > FECHAMENTO:
        return f"Os espaços funcionam das {ABERTURA} às {FECHAMENTO}."
    agora_dt = agora()
    if data < agora_dt.date() or (data == agora_dt.date() and fim <= agora_dt.strftime("%H:%M")):
        return "Esse horário já passou. Escolha uma data/horário futuro."
    return None


def datas_serie(dia, repeticoes):
    base = datetime.strptime(dia, "%Y-%m-%d")
    return [(base + timedelta(weeks=i)).strftime("%Y-%m-%d") for i in range(repeticoes)]


def sugerir_horarios(reservas, sala, dia, inicio, fim, limite=3):
    """Horários livres de mesma duração no mesmo espaço/dia, os mais próximos do pedido primeiro."""
    dur = hm(fim) - hm(inicio)
    ref = hm(inicio)
    agora_dt = agora()
    min_agora = agora_dt.hour * 60 + agora_dt.minute if dia == agora_dt.strftime("%Y-%m-%d") else 0
    candidatos = []
    for ini in range(hm(ABERTURA), hm(FECHAMENTO) - dur + 1, 30):
        if ini < min_agora:
            continue
        if not conflita(reservas, sala, dia, fmt(ini), fmt(ini + dur)):
            candidatos.append(ini)
    candidatos.sort(key=lambda x: abs(x - ref))
    return [(fmt(i), fmt(i + dur)) for i in sorted(candidatos[:limite])]


def espacos_livres(salas, reservas, dia, inicio, fim, minimo=1, tipo="", unidade=""):
    """Espaços livres no período, com capacidade/tipo/unidade compatíveis."""
    out = []
    for s in salas:
        if (s.capacidade or 0) < minimo:
            continue
        if tipo and s.tipo != tipo:
            continue
        if unidade and s.unidade != unidade:
            continue
        if not conflita(reservas, s.nome, dia, inicio, fim):
            out.append(s)
    return out


def status_reserva(r, ref=None):
    """'andamento' | 'proxima' | 'concluida'."""
    ref = ref or agora()
    hoje, hora = ref.strftime("%Y-%m-%d"), ref.strftime("%H:%M")
    if r["dia"] < hoje or (r["dia"] == hoje and r["fim"] <= hora):
        return "concluida"
    if r["dia"] == hoje and r["inicio"] <= hora < r["fim"]:
        return "andamento"
    return "proxima"


def situacao_espaco(reservas, sala, ref=None):
    """Situação em tempo real de um espaço: ocupado/livre + até quando + próxima reserva."""
    ref = ref or agora()
    hoje, hora = ref.strftime("%Y-%m-%d"), ref.strftime("%H:%M")
    do_dia = sorted((r for r in reservas if r["sala"] == sala and r["dia"] == hoje), key=lambda r: r["inicio"])
    atual = next((r for r in do_dia if r["inicio"] <= hora < r["fim"]), None)
    if atual:
        # encadeia reservas coladas para dizer "ocupada até"
        fim = atual["fim"]
        for r in do_dia:
            if r["inicio"] == fim:
                fim = r["fim"]
        return {"ocupada": True, "ate": fim, "por": atual.get("nome"), "titulo": atual.get("titulo")}
    prox = next((r for r in do_dia if r["inicio"] > hora), None)
    return {"ocupada": False, "ate": prox["inicio"] if prox else None, "por": None, "titulo": None}


def ocupacao_hoje(reservas, sala, dia):
    horas = sum((hm(r["fim"]) - hm(r["inicio"])) / 60 for r in reservas if r["sala"] == sala and r["dia"] == dia)
    return min(100, int(horas / JANELA_HORAS * 100))


def estatisticas(reservas, salas, ref=None):
    """Métricas reais para a página de relatórios."""
    ref = ref or agora()
    hoje = ref.date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)

    def horas(r):
        return (hm(r["fim"]) - hm(r["inicio"])) / 60

    por_hora = {h: 0 for h in range(7, 22)}
    for r in reservas:
        for h in range(hm(r["inicio"]) // 60, (hm(r["fim"]) + 59) // 60):
            if h in por_hora:
                por_hora[h] += 1
    pico = max(por_hora, key=por_hora.get) if any(por_hora.values()) else None

    por_sala = {s.nome: 0.0 for s in salas}
    por_unidade, por_pessoa = {}, {}
    for r in reservas:
        por_sala[r["sala"]] = por_sala.get(r["sala"], 0) + horas(r)
        sala = next((s for s in salas if s.nome == r["sala"]), None)
        un = sala.unidade if sala else "—"
        por_unidade[un] = por_unidade.get(un, 0) + horas(r)
        por_pessoa[r.get("nome") or r["email"]] = por_pessoa.get(r.get("nome") or r["email"], 0) + 1

    semana = [r for r in reservas
             if inicio_semana <= datetime.strptime(r["dia"], "%Y-%m-%d").date() <= fim_semana]
    ranking = sorted(por_sala.items(), key=lambda kv: kv[1], reverse=True)
    ociosos = [n for n, h in por_sala.items() if h == 0]
    return {
        "total": len(reservas),
        "horas_total": round(sum(horas(r) for r in reservas), 1),
        "semana": len(semana),
        "pico": f"{pico:02d}:00" if pico is not None else "—",
        "por_hora": por_hora,
        "max_hora": max(por_hora.values()) or 1,
        "ranking": ranking,
        "max_sala": (ranking[0][1] if ranking and ranking[0][1] else 1),
        "mais_usado": ranking[0][0] if ranking and ranking[0][1] else "—",
        "ociosos": ociosos,
        "por_unidade": sorted(por_unidade.items(), key=lambda kv: kv[1], reverse=True),
        "max_unidade": max(por_unidade.values()) if por_unidade else 1,
        "top_pessoas": sorted(por_pessoa.items(), key=lambda kv: kv[1], reverse=True)[:5],
    }


def gerar_ics(reservas):
    """Calendário .ics (compatível com Google Agenda, Outlook, Apple Calendar)."""
    def dt(dia, h):
        return dia.replace("-", "") + "T" + h.replace(":", "") + "00"

    linhas = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//OcupaSala//PT-BR", "CALSCALE:GREGORIAN"]
    carimbo = agora().strftime("%Y%m%dT%H%M%S")
    for r in reservas:
        resumo = (r.get("titulo") or "Reserva") + " — " + r["sala"]
        linhas += ["BEGIN:VEVENT", f"UID:{r['id']}@ocupasala", f"DTSTAMP:{carimbo}",
                   f"DTSTART;TZID=America/Sao_Paulo:{dt(r['dia'], r['inicio'])}",
                   f"DTEND;TZID=America/Sao_Paulo:{dt(r['dia'], r['fim'])}",
                   f"SUMMARY:{resumo}", f"LOCATION:{r['sala']}", "END:VEVENT"]
    linhas.append("END:VCALENDAR")
    return "\r\n".join(linhas) + "\r\n"
