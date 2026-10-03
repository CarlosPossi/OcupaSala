from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, flash, Response
from . import views_bp
from auth.routes import login_required
from models.utils import USERS_FILE, RESERVAS_FILE, load_json, save_json, agora
from models.entidades import Reserva, Usuario, listar_salas, get_sala_by_nome, criar_sala, remover_sala
from models import servicos as sv


def _iniciais(nome):
    partes = (nome or "?").split()
    return (partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")).upper()


@views_bp.app_context_processor
def contexto_global():
    return {"iniciais": _iniciais(session.get("user_nome"))}


# ------------------------------------------------------------------ DASHBOARD
@views_bp.route("/dashboard")
@login_required
def dashboard():
    reservas = sv.carregar_reservas()
    salas = listar_salas()
    ref = agora()
    hoje, hora = ref.strftime("%Y-%m-%d"), ref.strftime("%H:%M")
    email = session.get("user_email")

    situacao = {s.nome: sv.situacao_espaco(reservas, s.nome, ref) for s in salas}
    ocupadas = [n for n, st in situacao.items() if st["ocupada"]]
    ocupacao = {s.nome: sv.ocupacao_hoje(reservas, s.nome, hoje) for s in salas}

    minhas = [r for r in reservas if r["email"] == email]
    proximas = sorted((r for r in minhas if sv.status_reserva(r, ref) != "concluida"),
                      key=lambda r: (r["dia"], r["inicio"]))
    agenda_hoje = sorted((r for r in reservas if r["dia"] == hoje and r["fim"] > hora),
                         key=lambda r: r["inicio"])
    media_ocup = int(sum(ocupacao.values()) / len(ocupacao)) if ocupacao else 0

    return render_template("dashboard.html", nome=session.get("user_nome"), salas=salas,
                           situacao=situacao, ocupacao=ocupacao, total_salas=len(salas),
                           livres=len(salas) - len(ocupadas), media_ocup=media_ocup,
                           proxima=proximas[0] if proximas else None, minhas_proximas=len(proximas),
                           agenda_hoje=agenda_hoje[:6], hoje=hoje, hora=hora,
                           reservas_hoje=len([r for r in reservas if r["dia"] == hoje]))


# ------------------------------------------------------------------ RESERVAR
def _form_reserva(**extra):
    q = request.values
    dados = {"sala": q.get("sala", ""), "dia": q.get("dia") or agora().strftime("%Y-%m-%d"),
             "inicio": q.get("inicio", ""), "fim": q.get("fim", ""), "titulo": q.get("titulo", ""),
             "participantes": q.get("participantes", ""), "repetir": q.get("repetir", "1")}
    return render_template("reservar.html", salas=listar_salas(), f=dados,
                           hoje=agora().strftime("%Y-%m-%d"), **extra)


@views_bp.route("/reservar", methods=["GET", "POST"])
@login_required
def reservar():
    if request.method == "GET":
        return _form_reserva()

    sala_nome = request.form.get("sala")
    dia, inicio, fim = request.form.get("dia"), request.form.get("inicio"), request.form.get("fim")
    titulo = (request.form.get("titulo") or "").strip()[:80]
    sala = get_sala_by_nome(sala_nome)
    try:
        pessoas = max(1, int(request.form.get("participantes") or 1))
        repeticoes = min(12, max(1, int(request.form.get("repetir") or 1)))
    except ValueError:
        pessoas, repeticoes = 1, 1

    erro = sv.validar_periodo(dia, inicio, fim)
    if not sala:
        erro = "Selecione um espaço válido."
    elif not erro and pessoas > (sala.capacidade or 0):
        erro = f"{sala.nome} comporta no máximo {sala.capacidade} pessoa(s). Escolha um espaço maior."
    if erro:
        flash("❌ " + erro, "error")
        return _form_reserva()

    reservas = sv.carregar_reservas()
    datas = sv.datas_serie(dia, repeticoes)
    conflitos = [(d, sv.conflita(reservas, sala.nome, d, inicio, fim)) for d in datas]
    conflitos = [(d, c) for d, c in conflitos if c]

    if conflitos:
        d0, c0 = conflitos[0]
        datas_txt = ", ".join(datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m") for d, _ in conflitos)
        flash(f"❌ Conflito! {sala.nome} já está reservado em {datas_txt} "
              f"({c0['inicio']}–{c0['fim']}, {c0.get('titulo') or 'reserva existente'}).", "error")
        salas = listar_salas()
        alternativas = sv.espacos_livres(salas, reservas, dia, inicio, fim, minimo=pessoas)
        alternativas = sorted((s for s in alternativas if s.nome != sala.nome), key=lambda s: s.capacidade)
        return _form_reserva(sugestoes_horario=sv.sugerir_horarios(reservas, sala.nome, dia, inicio, fim),
                             sugestoes_espaco=alternativas[:4])

    serie = Reserva(None, None, None, None, None).id if repeticoes > 1 else None
    criadas = agora().isoformat(timespec="seconds")
    for d in datas:
        reservas.append(Reserva(sala.nome, d, inicio, fim, session["user_email"], session["user_nome"],
                                titulo, pessoas, serie, criada_em=criadas).to_dict())
    save_json(RESERVAS_FILE, reservas)
    msg = "✅ Reserva confirmada!" if repeticoes == 1 else f"✅ {repeticoes} reservas semanais confirmadas!"
    flash(msg, "success")
    return redirect(url_for("views.reservas_view"))


# ------------------------------------------------------------------ BUSCAR ESPAÇO LIVRE
@views_bp.route("/disponibilidade")
@login_required
def disponibilidade():
    q = request.args
    salas = listar_salas()
    f = {"dia": q.get("dia") or agora().strftime("%Y-%m-%d"), "inicio": q.get("inicio", ""),
         "fim": q.get("fim", ""), "minimo": q.get("minimo", ""), "tipo": q.get("tipo", ""),
         "unidade": q.get("unidade", "")}
    resultado = None
    if q.get("buscar"):
        erro = sv.validar_periodo(f["dia"], f["inicio"], f["fim"])
        if erro:
            flash("❌ " + erro, "error")
        else:
            try:
                minimo = max(1, int(f["minimo"] or 1))
            except ValueError:
                minimo = 1
            livres = sv.espacos_livres(salas, sv.carregar_reservas(), f["dia"], f["inicio"], f["fim"],
                                       minimo, f["tipo"], f["unidade"])
            # os que "cabem melhor" (menor sobra de capacidade) vêm primeiro
            resultado = sorted(livres, key=lambda s: s.capacidade - minimo)
    return render_template("disponibilidade.html", f=f, resultado=resultado,
                           tipos=sorted({s.tipo for s in salas}), unidades=sorted({s.unidade for s in salas}),
                           hoje=agora().strftime("%Y-%m-%d"))


# ------------------------------------------------------------------ AGENDA (linha do tempo)
@views_bp.route("/agenda")
@login_required
def agenda():
    ref = agora()
    dia = request.args.get("dia") or ref.strftime("%Y-%m-%d")
    try:
        data = datetime.strptime(dia, "%Y-%m-%d")
    except ValueError:
        data = datetime.strptime(ref.strftime("%Y-%m-%d"), "%Y-%m-%d")
        dia = data.strftime("%Y-%m-%d")
    reservas = [r for r in sv.carregar_reservas() if r["dia"] == dia]
    salas = listar_salas()
    ini, fim = sv.hm(sv.ABERTURA), sv.hm(sv.FECHAMENTO)
    total = fim - ini
    linhas = []
    for s in salas:
        blocos = []
        for r in sorted((x for x in reservas if x["sala"] == s.nome), key=lambda x: x["inicio"]):
            blocos.append({**r, "esq": (sv.hm(r["inicio"]) - ini) / total * 100,
                           "larg": (sv.hm(r["fim"]) - sv.hm(r["inicio"])) / total * 100,
                           "meu": r["email"] == session["user_email"]})
        linhas.append({"sala": s, "blocos": blocos})
    agora_pct = None
    if dia == ref.strftime("%Y-%m-%d"):
        m = ref.hour * 60 + ref.minute
        if ini <= m <= fim:
            agora_pct = (m - ini) / total * 100
    return render_template("agenda.html", dia=dia, data=data, linhas=linhas, agora_pct=agora_pct,
                           horas=list(range(ini // 60, fim // 60 + 1)), n_horas=fim // 60 - ini // 60,
                           anterior=(data - timedelta(days=1)).strftime("%Y-%m-%d"),
                           proximo=(data + timedelta(days=1)).strftime("%Y-%m-%d"),
                           hoje=ref.strftime("%Y-%m-%d"))


# ------------------------------------------------------------------ QUADRO DE RESERVAS
@views_bp.route("/reservas")
@login_required
def reservas_view():
    ref = agora()
    visao = request.args.get("visao", "proximas")  # proximas | minhas | todas | concluidas
    reservas = sv.carregar_reservas()
    for r in reservas:
        r["status"] = sv.status_reserva(r, ref)
    email = session["user_email"]
    if visao == "minhas":
        lista = [r for r in reservas if r["email"] == email]
    elif visao == "concluidas":
        lista = [r for r in reservas if r["status"] == "concluida"]
    elif visao == "todas":
        lista = reservas
    else:
        lista = [r for r in reservas if r["status"] != "concluida"]
    lista.sort(key=lambda r: (r["dia"], r["inicio"]), reverse=(visao == "concluidas"))
    contagem = {"proximas": sum(r["status"] != "concluida" for r in reservas),
                "minhas": sum(r["email"] == email for r in reservas),
                "concluidas": sum(r["status"] == "concluida" for r in reservas), "todas": len(reservas)}
    return render_template("reservas.html", reservas=lista, user_email=email, visao=visao, contagem=contagem)


@views_bp.route("/cancelar", methods=["POST"])
@login_required
def cancelar():
    rid, escopo = request.form.get("id"), request.form.get("escopo", "uma")
    email = session["user_email"]
    reservas = sv.carregar_reservas()
    alvo = next((r for r in reservas if r["id"] == rid and r["email"] == email), None)
    if not alvo:
        flash("❌ Reserva não encontrada ou sem permissão para cancelar.", "error")
        return redirect(url_for("views.reservas_view"))
    if escopo == "serie" and alvo.get("serie_id"):
        nova = [r for r in reservas if not (r.get("serie_id") == alvo["serie_id"] and r["email"] == email
                                            and r["dia"] >= alvo["dia"])]
    else:
        nova = [r for r in reservas if r["id"] != rid]
    save_json(RESERVAS_FILE, nova)
    n = len(reservas) - len(nova)
    flash("✅ Reserva cancelada." if n == 1 else f"✅ {n} reservas da série canceladas.", "success")
    return redirect(request.referrer or url_for("views.reservas_view"))


@views_bp.route("/reservas/exportar.ics")
@login_required
def exportar_ics():
    ref = agora()
    minhas = [r for r in sv.carregar_reservas()
              if r["email"] == session["user_email"] and sv.status_reserva(r, ref) != "concluida"]
    return Response(sv.gerar_ics(minhas), mimetype="text/calendar",
                    headers={"Content-Disposition": "attachment; filename=ocupasala-minha-agenda.ics"})


# ------------------------------------------------------------------ ESPAÇOS
@views_bp.route("/espacos", methods=["GET", "POST"])
@login_required
def espacos():
    if request.method == "POST":
        ok, msg = criar_sala(request.form.get("nome"), request.form.get("tipo"),
                             request.form.get("unidade"), request.form.get("capacidade"))
        flash(("✅ " if ok else "❌ ") + msg, "success" if ok else "error")
        return redirect(url_for("views.espacos"))
    por_sala = {}
    for r in sv.carregar_reservas():
        por_sala[r["sala"]] = por_sala.get(r["sala"], 0) + 1
    return render_template("espacos.html", salas=listar_salas(), reservas_por_sala=por_sala)


@views_bp.route("/espacos/excluir", methods=["POST"])
@login_required
def excluir_espaco():
    ok, msg = remover_sala(request.form.get("nome"), sv.carregar_reservas())
    flash(("✅ " if ok else "❌ ") + msg, "success" if ok else "error")
    return redirect(url_for("views.espacos"))


# ------------------------------------------------------------------ RELATÓRIOS / CONFIG
@views_bp.route("/relatorios")
@login_required
def relatorios():
    return render_template("relatorios.html", e=sv.estatisticas(sv.carregar_reservas(), listar_salas()))


@views_bp.route("/configuracoes", methods=["GET", "POST"])
@login_required
def configuracoes():
    if request.method == "POST":
        email = session["user_email"]
        users = load_json(USERS_FILE)
        u = next((x for x in users if x["email"] == email), None)
        acao = request.form.get("acao")
        if acao == "perfil":
            nome = (request.form.get("nome") or "").strip()
            if len(nome) < 2:
                flash("❌ Informe um nome válido.", "error")
            else:
                u["nome"] = nome
                save_json(USERS_FILE, users)
                reservas = sv.carregar_reservas()
                for r in reservas:
                    if r["email"] == email:
                        r["nome"] = nome
                save_json(RESERVAS_FILE, reservas)
                session["user_nome"] = nome
                flash("✅ Perfil atualizado.", "success")
        elif acao == "senha":
            usuario = Usuario.from_dict(u)
            nova = request.form.get("nova") or ""
            if not usuario.verificar_senha(request.form.get("atual") or ""):
                flash("❌ Senha atual incorreta.", "error")
            elif len(nova) < 6:
                flash("❌ A nova senha precisa ter pelo menos 6 caracteres.", "error")
            else:
                u["senha"] = Usuario(u["nome"], email, nova).senha_hash
                save_json(USERS_FILE, users)
                flash("✅ Senha alterada com sucesso.", "success")
        return redirect(url_for("views.configuracoes"))
    return render_template("configuracoes.html")
