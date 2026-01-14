from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
from app import db 
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Lavoro40, Lavoro50, LavoroAdmin, User, Cliente
from dateutil.relativedelta import relativedelta

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    # --- HELPER PER TIMELINE (Ultimi 3 mesi) ---
    def get_timeline_data(model_list):
        # model_list è una lista di classi DB da interrogare (es. [Lavoro40, Lavoro50])
        now = datetime.now()
        months_data = []
        colors = ['var(--primary)', '#ff9f43', '#00A651'] # Blu, Arancio, Verde
        
        # Calcoliamo per mese corrente (0), mese scorso (1), due mesi fa (2)
        max_count = 0
        for i in range(3):
            # Data di inizio e fine del mese 'i'
            target_date = now - relativedelta(months=i)
            month_name = target_date.strftime('%B') # Nome mese (es. October)
            
            # Traduzione semplice (opzionale, o usa locale)
            mesi_it = {'January':'Gen', 'February':'Feb', 'March':'Mar', 'April':'Apr', 'May':'Mag', 'June':'Giu',
                       'July':'Lug', 'August':'Ago', 'September':'Set', 'October':'Ott', 'November':'Nov', 'December':'Dic'}
            month_label = mesi_it.get(month_name, month_name)

            # Conta lavori creati in quel mese e anno
            count = 0
            for model in model_list:
                # Metodo semplice compatibile con tutto:
                start_dt = datetime(target_date.year, target_date.month, 1)
                if target_date.month == 12:
                    end_dt = datetime(target_date.year + 1, 1, 1)
                else:
                    end_dt = datetime(target_date.year, target_date.month + 1, 1)
                
                # Nota: Assicurarsi che i modelli abbiano il campo created_at, altrimenti usare data_contatto o simile
                if hasattr(model, 'created_at'):
                    c = model.query.filter(model.created_at >= start_dt, model.created_at < end_dt).count()
                    count += c

            if count > max_count:
                max_count = count
            
            months_data.append({
                'label': month_label,
                'count': count,
                'color': colors[i]
            })
        
        # Calcolo percentuali larghezza barre
        for m in months_data:
            if max_count > 0:
                m['width'] = (m['count'] / max_count) * 100
            else:
                m['width'] = 0
                
        return months_data 

    # --- LOGICA DASHBOARD ---
    timeline = []
    
    # --- LOGICA PER ADMIN ---
    if current_user.role == 'admin':
        # TIMELINE ADMIN (Basata su LavoroAdmin)
        timeline = get_timeline_data([LavoroAdmin])
        
        # 1. Calcolo Fatturati (Widget Rosso)
        # Nota: Adatta i nomi dei campi quota se nel model nuovo si chiamano c_fe, c_amin ecc.
        # Qui mantengo la logica dashboard esistente, assumendo che per la visualizzazione usi ancora questi campi
        # o che tu abbia mappato le property nel model.
        tot_fe = db.session.query(func.sum(LavoroAdmin.c_fe)).scalar() or 0
        tot_amin = db.session.query(func.sum(LavoroAdmin.c_amin)).scalar() or 0
        tot_galvan = db.session.query(func.sum(LavoroAdmin.c_galvan)).scalar() or 0
        tot_fh = db.session.query(func.sum(LavoroAdmin.c_fh)).scalar() or 0
        # tot_capr = db.session.query(func.sum(LavoroAdmin.capriuolo_quota)).scalar() or 0 # Se esiste ancora
        
        total_lavori = LavoroAdmin.query.count()
        in_corso = LavoroAdmin.query.filter(LavoroAdmin.stato.ilike('In corso')).count()
        completati = LavoroAdmin.query.filter(LavoroAdmin.stato.in_(['Fatturato', 'Completo', 'Chiuso'])).count()
        
        return render_template('main/dashboard.html',
                               role='admin',
                               tot_fe=tot_fe, tot_amin=tot_amin, tot_galvan=tot_galvan, tot_fh=tot_fh,
                               total_lavori=total_lavori, in_corso=in_corso, completati=completati,
                               timeline=timeline)

    else:
        # TIMELINE BASE (Basata su Lavoro40 + Lavoro50)
        timeline = get_timeline_data([Lavoro40, Lavoro50])
        # Conteggi totali
        count_40 = Lavoro40.query.count()
        count_50 = Lavoro50.query.count()
        total_lavori = count_40 + count_50
        in_corso = Lavoro40.query.filter_by(esito='In corso').count()
        completati = Lavoro40.query.filter(Lavoro40.esito.in_(['Completo', 'Fatturato'])).count()
        fatturato_query = db.session.query(func.sum(Lavoro40.compenso)).scalar()
        fatturato_totale = fatturato_query or 0

        return render_template('main/dashboard.html', 
                               role='base',
                               total_lavori=total_lavori, in_corso=in_corso, completati=completati, fatturato=fatturato_totale,
                               timeline=timeline)

# --- API E ROTTE ADMIN (NUOVE FUNZIONALITÀ) ---

@bp.route('/api/clienti')
@login_required
def api_clienti():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    # Cerca clienti simili
    clienti = Cliente.query.filter(Cliente.nome.ilike(f'%{query}%')).limit(10).all()
    results = []
    for c in clienti:
        results.append({
            'nome': c.nome,
            'p_iva': c.p_iva,
            'indirizzo': c.indirizzo,
            'civico': c.civico,
            'cap': c.cap,
            'comune': c.comune,
            'provincia': c.provincia,
            'pec': c.pec
        })
    return jsonify(results)

@bp.route('/lavori_admin')
@login_required
def lavori_admin():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
        
    view_mode = current_user.admin_view_mode
    if view_mode == 'extra2':
        view_mode = 'standard'
    
    # MODIFICA: .asc() invece di .desc()
    lavori = LavoroAdmin.query.order_by(LavoroAdmin.numero.asc()).all()
    
    return render_template('main/lavori_admin.html', lavori=lavori, view_mode=view_mode)
    
# NUOVA ROTTA SPECIALE (Sostituto Firma - Solo per Extra 2)
@bp.route('/lavori_focus')
@login_required
def lavori_focus():
    if current_user.role != 'admin' or current_user.admin_view_mode != 'extra2':
        return redirect(url_for('main.dashboard'))
    
    lavori = LavoroAdmin.query.order_by(LavoroAdmin.numero.asc()).all()
    
    return render_template('main/lavori_admin.html', lavori=lavori, view_mode='focus_special')

@bp.route('/add_lavoro_admin', methods=['POST'])
@login_required
def add_lavoro_admin():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))

    # 1. GESTIONE CLIENTE (Salva o Aggiorna)
    nome_cliente = request.form.get('cliente_nome')
    cliente = Cliente.query.filter_by(nome=nome_cliente).first()
    
    if not cliente:
        cliente = Cliente(
            nome=nome_cliente,
            p_iva=request.form.get('cliente_piva'),
            indirizzo=request.form.get('cliente_indirizzo'),
            civico=request.form.get('cliente_civico'),
            cap=request.form.get('cliente_cap'),
            comune=request.form.get('cliente_comune'),
            provincia=request.form.get('cliente_provincia'),
            pec=request.form.get('cliente_pec')
        )
        db.session.add(cliente)
        db.session.flush() # Per avere l'ID subito
    
    # 2. NUMERO SEQUENZIALE
    last = LavoroAdmin.query.order_by(LavoroAdmin.numero.desc()).first()
    new_num = (last.numero + 1) if (last and last.numero) else 1

    # 3. CREAZIONE LAVORO
    try:
        # Helper per convertire float
        def to_float(val):
            try:
                # Gestione stringhe con formattazione italiana (es. 1.234,56)
                if isinstance(val, str):
                    val = val.replace('.', '').replace(',', '.')
                return float(val)
            except: 
                return 0.0

        # --- GESTIONE BENI MULTIPLI ---
        beni_descrizioni = []
        valore_totale_beni = 0.0
        
        # Itera sui beni inviati dal form (beni[0], beni[1], ecc.)
        i = 0
        while True:
            desc_key = f'beni[{i}][descrizione]'
            val_key = f'beni[{i}][valore]'
            
            # Se non esiste la chiave per l'indice corrente, interrompi il ciclo
            if desc_key not in request.form:
                break
                
            descrizione = request.form.get(desc_key, '').strip()
            valore_str = request.form.get(val_key, '0')
            
            # Converti valore
            valore = to_float(valore_str)
            
            if descrizione:
                beni_descrizioni.append(descrizione)
                valore_totale_beni += valore
                
            i += 1

        # Genera stringa concatenata (es. "Appartamento A | Box Auto")
        # Se non ci sono beni multipli, tenta un fallback sul campo singolo 'bene' vecchio stile, se presente
        if beni_descrizioni:
            bene_concatenato = ' | '.join(beni_descrizioni)
        else:
            bene_concatenato = request.form.get('bene', '') # Fallback

        # Se il valore totale calcolato è 0, controlla se c'è un valore singolo inserito (fallback)
        if valore_totale_beni == 0.0 and request.form.get('valore_bene'):
            valore_totale_beni = to_float(request.form.get('valore_bene'))

        # Creazione Oggetto DB
        nuovo = LavoroAdmin(
            numero=new_num,
            cliente_id=cliente.id,
            cliente_nome=nome_cliente,
            
            # --- CAMPI MODIFICATI ---
            bene=bene_concatenato, 
            valore_bene=valore_totale_beni,
            # ------------------------

            importo_offerta=to_float(request.form.get('importo_offerta')),
            
            origine=request.form.get('origine'),
            nome_esterno=request.form.get('nome_esterno'),
            redattore=request.form.get('redattore'),
            collaboratore=request.form.get('collaboratore'),

            # Checkbox Ruoli
            has_revisore=(request.form.get('has_revisore') == 'on'),
            has_caricamento=(request.form.get('has_caricamento') == 'on'),

            # Compensi
            c_fe=to_float(request.form.get('c_fe')),
            c_amin=to_float(request.form.get('c_amin')),
            c_galvan=to_float(request.form.get('c_galvan')),
            c_fh=to_float(request.form.get('c_fh')),
            c_bianc=to_float(request.form.get('c_bianc')),
            c_ext=to_float(request.form.get('c_ext')),
            c_revisore=to_float(request.form.get('c_revisore')),
            c_caricamento=to_float(request.form.get('c_caricamento')),

            stato='In corso' # Default
        )
        
        db.session.add(nuovo)
        db.session.commit()
        flash('Lavoro Admin aggiunto con successo!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Errore salvataggio: {str(e)}', 'error')

    return redirect(url_for('main.lavori_admin'))
    
# Valori italiani
def to_float_it(val):
    """Converte un valore formattato italiano (1.234,56) in float"""
    if not val:
        return 0.0
    try:
        # Rimuovi punti (separatore migliaia) e sostituisci virgola con punto
        cleaned = str(val).replace('.', '').replace(',', '.')
        return float(cleaned)
    except:
        return 0.0

@bp.route('/update_lavoro_field/<int:id>', methods=['POST'])
@login_required
def update_lavoro_field(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    lavoro = LavoroAdmin.query.get_or_404(id)
    data = request.json
    field = data.get('field')
    value = data.get('value')

    if field == 'stato':
        lavoro.stato = value
    elif field == 'data_offerta_check':
        lavoro.data_offerta_check = value
    elif field == 'data_offerta':
        if value: lavoro.data_offerta = datetime.strptime(value, '%Y-%m-%d').date()
        else: lavoro.data_offerta = None
    elif field == 'data_firma_check':
        lavoro.data_firma_check = value
    elif field == 'data_firma':
        if value: lavoro.data_firma = datetime.strptime(value, '%Y-%m-%d').date()
        else: lavoro.data_firma = None
    elif field == 'data_pec':
        if value: lavoro.data_pec = datetime.strptime(value, '%Y-%m-%d').date()
    
    # Eventuale gestione altri campi inline...

    db.session.commit()
    return jsonify({'success': True})
    
@bp.route('/delete_lavoro_admin/<int:id>', methods=['POST'])
@login_required
def delete_lavoro_admin(id):
    if current_user.role != 'admin':
        flash('Accesso negato.', 'error')
        return redirect(url_for('main.dashboard'))
    
    lavoro = LavoroAdmin.query.get_or_404(id)
    db.session.delete(lavoro)
    db.session.commit()
    
    flash(f'Lavoro #{id} eliminato con successo.', 'success')
    return redirect(url_for('main.lavori_admin'))


# --- ROTTE BASE (Lavori 4.0 / 5.0) ---

@bp.route('/lavori')
@login_required
def lavori():
    # Se un admin prova ad accedere qui, lo mandiamo alla sua pagina
    if current_user.role == 'admin':
        return redirect(url_for('main.lavori_admin'))

    tipo_lavoro = request.args.get('tipo', '40')
    
    if tipo_lavoro == '50':
        items = Lavoro50.query.all()
    else:
        items = Lavoro40.query.all()
        
    return render_template('main/lavori.html', items=items, tipo=tipo_lavoro)

@bp.route('/add_lavoro', methods=['POST'])
@login_required
def add_lavoro():
    tipo = request.form.get('tipo')
    cliente = request.form.get('cliente')
    bene = request.form.get('bene')
    note = request.form.get('note')
    
    is_contattato = request.form.get('contattato') == 'on'
    data_str = request.form.get('data_contatto')
    data_obj = None
    if is_contattato and data_str:
        try:
            data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        except:
            pass

    if tipo == '40':
        last = Lavoro40.query.order_by(Lavoro40.numero.desc()).first()
        new_num = (last.numero + 1) if last and last.numero else 1
        esito = request.form.get('esito')
        
        nuovo = Lavoro40(
            numero=new_num,
            cliente=cliente,
            bene=bene,
            contattato=is_contattato,
            data_contatto=data_obj,
            note=note,
            esito=esito,
            sollecito=False
        )
        db.session.add(nuovo)
        
    elif tipo == '50':
        last = Lavoro50.query.order_by(Lavoro50.numero.desc()).first()
        new_num = (last.numero + 1) if last and last.numero else 1
        codice = request.form.get('codice')
        
        nuovo = Lavoro50(
            numero=new_num,
            cliente=cliente,
            bene=bene,
            contattato=is_contattato,
            data_contatto=data_obj,
            note=note,
            codice=codice
        )
        db.session.add(nuovo)

    db.session.commit()
    return redirect(url_for('main.lavori', tipo=tipo))

@bp.route('/delete_lavoro/<int:id>', methods=['POST'])
@login_required
def delete_lavoro(id):
    tipo = request.args.get('tipo', '40')
    if tipo == '40':
        lavoro = Lavoro40.query.get_or_404(id)
    else:
        lavoro = Lavoro50.query.get_or_404(id)
    db.session.delete(lavoro)
    db.session.commit()
    return redirect(url_for('main.lavori', tipo=tipo))

@bp.route('/edit_lavoro/<int:id>', methods=['POST'])
@login_required
def edit_lavoro(id):
    tipo = request.form.get('tipo')
    if tipo == '40':
        lavoro = Lavoro40.query.get_or_404(id)
        lavoro.esito = request.form.get('esito')
        lavoro.sollecito = True if request.form.get('sollecito') == 'on' else False
        try:
            lavoro.compenso = float(request.form.get('compenso'))
        except:
            lavoro.compenso = 0.0
    else:
        lavoro = Lavoro50.query.get_or_404(id)
        lavoro.ex_ante = request.form.get('ex_ante')
        lavoro.perc_20 = True if request.form.get('perc_20') == 'on' else False
        lavoro.ex_post = request.form.get('ex_post')
        lavoro.codice = request.form.get('codice')

    lavoro.cliente = request.form.get('cliente')
    lavoro.bene = request.form.get('bene')
    lavoro.note = request.form.get('note')
    
    is_contattato = request.form.get('contattato') == 'on'
    lavoro.contattato = is_contattato
    data_str = request.form.get('data_contatto')
    if is_contattato and data_str:
        try:
            lavoro.data_contatto = datetime.strptime(data_str, '%Y-%m-%d').date()
        except:
            pass
    elif not is_contattato:
        lavoro.data_contatto = None

    db.session.commit()
    return redirect(url_for('main.lavori', tipo=tipo))

@bp.route('/calendario')
@login_required
def calendario():
    eventi = []
    # Eventi 4.0
    for l in Lavoro40.query.filter(Lavoro40.data_contatto != None).all():
        eventi.append({
            'title': f"4.0 - {l.cliente}",
            'start': l.data_contatto.strftime('%Y-%m-%d'),
            'color': '#007AFF',
            'url': url_for('main.lavori', tipo='40')
        })
    # Eventi 5.0
    for l in Lavoro50.query.filter(Lavoro50.data_contatto != None).all():
        eventi.append({
            'title': f"5.0 - {l.cliente}",
            'start': l.data_contatto.strftime('%Y-%m-%d'),
            'color': '#00A651',
            'url': url_for('main.lavori', tipo='50')
        })
    return render_template('main/calendario.html', eventi=eventi)
    
@bp.route('/impostazioni')
@login_required
def impostazioni():
    # Se sei admin, ti passo anche la lista di tutti gli utenti per poterli gestire
    users = []
    if current_user.role == 'admin':
        users = User.query.all()
    
    return render_template('main/impostazioni.html', users=users)
    
@bp.route('/save_view_mode', methods=['POST'])
@login_required
def save_view_mode():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    mode = request.form.get('view_mode')
    if mode in ['standard', 'extra1', 'extra2']:
        current_user.admin_view_mode = mode
        db.session.commit()
        flash('Modalità di visualizzazione aggiornata!', 'success')
    
    return redirect(url_for('main.impostazioni'))

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    old_pass = request.form.get('old_password')
    new_pass = request.form.get('new_password')
    confirm_pass = request.form.get('confirm_password')

    # 1. Verifica vecchia password
    if not check_password_hash(current_user.password_hash, old_pass):
        flash('La vecchia password non è corretta.', 'error')
        return redirect(url_for('main.impostazioni'))

    # 2. Verifica che le nuove coincidano
    if new_pass != confirm_pass:
        flash('Le nuove password non coincidono.', 'error')
        return redirect(url_for('main.impostazioni'))

    # 3. Aggiorna
    current_user.set_password(new_pass)
    db.session.commit()
    
    flash('Password aggiornata con successo!', 'success')
    return redirect(url_for('main.impostazioni'))

@bp.route('/admin_reset_password/<int:user_id>', methods=['POST'])
@login_required
def admin_reset_password(user_id):
    # Protezione: Solo Admin può farlo
    if current_user.role != 'admin':
        flash('Accesso negato.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    default_pass = "Ciao1234"
    user.set_password(default_pass)
    db.session.commit()
    
    flash(f'Password di {user.username} resettata a "{default_pass}"', 'success')
    return redirect(url_for('main.impostazioni'))
    
@bp.route('/api/esterni')
@login_required
def api_esterni():
    query = request.args.get('q', '')
    # Cerca solo se ci sono almeno 1 carattere
    if len(query) < 1:
        return jsonify([])
    
    # Cerca i nomi univoci nella colonna nome_esterno
    nomi = db.session.query(LavoroAdmin.nome_esterno)\
        .filter(LavoroAdmin.nome_esterno.ilike(f'%{query}%'))\
        .filter(LavoroAdmin.nome_esterno != None)\
        .filter(LavoroAdmin.nome_esterno != '')\
        .distinct().limit(10).all()
    
    # Restituisce una lista semplice di stringhe ['Nome1', 'Nome2']
    results = [n[0] for n in nomi]
    return jsonify(results)