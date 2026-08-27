from flask import render_template, request, redirect, url_for, session, flash
from datetime import datetime
from . import views_bp
from auth.routes import login_required
from models.utils import RESERVAS_FILE, load_json, save_json
from models.entidades import Reserva, CATALOGO_SALAS

@views_bp.route('/dashboard')
@login_required
def dashboard():
    reservas_data = load_json(RESERVAS_FILE)
    email_usuario = session.get('user_email')
    agora_dt = datetime.now()
    hoje = agora_dt.strftime("%Y-%m-%d")
    agora_hora = agora_dt.strftime("%H:%M")

    todas_salas = [sala.nome for sala in CATALOGO_SALAS]
    capacidades = {sala.nome: sala.capacidade for sala in CATALOGO_SALAS}

    # 1. Estatísticas Básicas
    total_reservas = len(reservas_data)
    salas_ocupadas_agora = [r['sala'] for r in reservas_data if r.get('dia') == hoje and r.get('inicio', '') <= agora_hora < r.get('fim', '')]
    salas_disponiveis_count = len(todas_salas) - len(set(salas_ocupadas_agora))
    
    # 2. Ocupação Hoje
    ocupacao = {}
    for sala in todas_salas:
        horas_reservadas = 0
        for r in reservas_data:
            if r.get('dia') == hoje and r['sala'] == sala:
                h1 = datetime.strptime(r['inicio'], "%H:%M")
                h2 = datetime.strptime(r['fim'], "%H:%M")
                horas_reservadas += (h2 - h1).seconds / 3600
        ocupacao[sala] = min(100, int((horas_reservadas / 12) * 100))
    
    # 3. Próxima Reserva e Atividades
    minhas_reservas = [r for r in reservas_data if r.get('email') == email_usuario and (r.get('dia') > hoje or (r.get('dia') == hoje and r.get('fim', '') > agora_hora))]
    minhas_reservas.sort(key=lambda x: (x['dia'], x['inicio']))
    
    minhas_atividades = [r for r in reservas_data if r.get('email') == email_usuario]
    minhas_atividades.sort(key=lambda x: (x['dia'], x['inicio']), reverse=True)
    
    return render_template('dashboard.html', 
                           nome=session.get('user_nome'), 
                           total_reservas=total_reservas,
                           salas_disponiveis=salas_disponiveis_count,
                           proxima_reserva=minhas_reservas[0] if minhas_reservas else None,
                           atividades=minhas_atividades[:5],
                           ocupacao=ocupacao,
                           salas_ocupadas_agora=salas_ocupadas_agora,
                           todas_salas=todas_salas,
                           capacidades=capacidades,
                           total_salas=len(todas_salas))

@views_bp.route('/relatorios')
@login_required
def relatorios():
    reservas = load_json(RESERVAS_FILE)
    return render_template('relatorios.html', total=len(reservas))

@views_bp.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('configuracoes.html')

@views_bp.route('/reservar', methods=['GET', 'POST'])
@login_required
def reservar():
    salas = CATALOGO_SALAS
    if request.method == 'POST':
        sala = request.form.get('sala')
        dia = request.form.get('dia')
        inicio = request.form.get('inicio')
        fim = request.form.get('fim')
        
        if not dia or not inicio or not fim or inicio >= fim:
            flash("❌ Dados inválidos! Verifique horários e data.", "error")
            return render_template('reservar.html', salas=salas)

        reservas_data = load_json(RESERVAS_FILE)
        
        conflito = any(
            r['sala'] == sala and r.get('dia') == dia and (inicio < r['fim'] and fim > r['inicio'])
            for r in reservas_data
        )
        
        if conflito:
            flash("❌ Conflito! Esta sala já está ocupada neste horário no dia selecionado.", "error")
        else:
            # Usando a classe Reserva
            nova_reserva = Reserva(
                sala=sala, 
                dia=dia, 
                inicio=inicio, 
                fim=fim, 
                email=session.get('user_email'),
                nome=session.get('user_nome')
            )
            reservas_data.append(nova_reserva.to_dict())
            save_json(RESERVAS_FILE, reservas_data)
            flash("✅ Reserva realizada com sucesso!", "success")
            return redirect(url_for('views.reservas_view'))
            
    return render_template('reservar.html', salas=salas)

@views_bp.route('/reservas')
@login_required
def reservas_view():
    reservas = load_json(RESERVAS_FILE)
    reservas.sort(key=lambda x: (x.get('dia', ''), x['sala'], x['inicio']))
    return render_template('reservas.html', reservas=reservas, user_email=session.get('user_email'))

@views_bp.route('/cancelar', methods=['POST'])
@login_required
def cancelar():
    sala = request.form.get('sala')
    dia = request.form.get('dia')
    inicio = request.form.get('inicio')
    fim = request.form.get('fim')
    email = session.get('user_email')
    
    reservas = load_json(RESERVAS_FILE)
    nova_lista = [
        r for r in reservas if not (
            r['sala'] == sala and 
            r.get('dia') == dia and 
            r['inicio'] == inicio and 
            r['fim'] == fim and 
            r['email'] == email
        )
    ]
    
    if len(nova_lista) < len(reservas):
        save_json(RESERVAS_FILE, nova_lista)
        flash("✅ Reserva cancelada!", "success")
    else:
        flash("❌ Erro ao cancelar reserva.", "error")
        
    return redirect(url_for('views.reservas_view'))

