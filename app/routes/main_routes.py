from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
from app import db 
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Lavoro40, Lavoro50, LavoroAdmin, User, Cliente, Bene
from dateutil.relativedelta import relativedelta
from pathlib import Path

from app.utils.offerta_docx import generate_offerta_docx, format_date_it_long


def _build_beni_list_for_offerta(lavoro: LavoroAdmin) -> list[dict]:
    beni_list: list[dict] = []
    if lavoro.beni_list:
        for bene in sorted(lavoro.beni_list, key=lambda x: x.ordine):
            beni_list.append({
                'id': bene.id,
                'descrizione': bene.descrizione,
                'valore': bene.valore,
                'importo_offerta': getattr(bene, 'importo_offerta', 0) or 0,
                'stato': getattr(bene, 'stato', 'vuoto') or 'vuoto',
                'data_pec': bene.data_pec.strftime('%Y-%m-%d') if getattr(bene, 'data_pec', None) else None
            })
    else:
        if lavoro.bene and ' | ' in lavoro.bene:
            beni_parts = lavoro.bene.split(' | ')
            valore_per_bene = lavoro.valore_bene / len(beni_parts) if len(beni_parts) > 0 else lavoro.valore_bene
            importo_per_bene = lavoro.importo_offerta / len(beni_parts) if len(beni_parts) > 0 else lavoro.importo_offerta
            for desc in beni_parts:
                beni_list.append({'id': None, 'descrizione': desc.strip(), 'valore': valore_per_bene, 'importo_offerta': importo_per_bene, 'stato': lavoro.stato, 'data_pec': lavoro.data_pec.strftime('%Y-%m-%d') if lavoro.data_pec else None})
        else:
            beni_list.append({'id': None, 'descrizione': lavoro.bene or '', 'valore': lavoro.valore_bene, 'importo_offerta': lavoro.importo_offerta, 'stato': lavoro.stato, 'data_pec': lavoro.data_pec.strftime('%Y-%m-%d') if lavoro.data_pec else None})
    return beni_list


def _generate_offerta_response(*, lavoro: LavoroAdmin, tipo: str) :
    cliente = Cliente.query.get(lavoro.cliente_id) if lavoro.cliente_id else None

    # Gestione template in base al tipo
    # Per "rsid" non ha variante _amm
    # Per "varie" ha variante _amm se ci sono spese amministrative
    if tipo == 'rsid':
        template_name = "off_rsid.docx"
    elif tipo == 'varie':
        suffix = "_amm" if getattr(lavoro, 'spese_amministrative', False) else ""
        template_name = f"off_varie{suffix}.docx"
    else:
        # Per "old" e "iper" mantieni la logica esistente
        suffix = "_amm" if getattr(lavoro, 'spese_amministrative', False) else ""
        template_name = f"off_{tipo}{suffix}.docx"
    
    template_path = Path(current_app.root_path) / "doc_templates" / "offerte" / template_name
    if not template_path.exists():
        return jsonify({'error': f"Template mancante: {template_name}"}), 404

    beni_list = _build_beni_list_for_offerta(lavoro)

    today = datetime.now().date()

    current_rev = int(getattr(lavoro, 'offerta_revision', 0) or 0)
    dirty = bool(getattr(lavoro, 'offerta_dirty', False))
    has_prev_offerta = bool(lavoro.data_offerta)

    rev_to_use = current_rev
    if has_prev_offerta and dirty:
        rev_to_use = current_rev + 1

    data_emissione_text = format_date_it_long(today)
    if rev_to_use > 0:
        data_emissione_text = f"{data_emissione_text} (rev. {rev_to_use})"

    cliente_nome = lavoro.cliente_nome or (cliente.nome if cliente else "")

    buf = generate_offerta_docx(
        template_path,
        cliente_nome=cliente_nome,
        indirizzo=(cliente.indirizzo if cliente else ""),
        civico=(cliente.civico if cliente else ""),
        cap=(cliente.cap if cliente else ""),
        comune=(cliente.comune if cliente else ""),
        prov=(cliente.provincia if cliente else ""),
        piva=(cliente.p_iva if cliente else ""),
        data_emissione_text=data_emissione_text,
        importo_caricamento=getattr(lavoro, 'importo_caricamento', 0) or 0,
        importo_revisione=getattr(lavoro, 'importo_revisione', 0) or 0,
        beni=beni_list,
    )

    lavoro.data_offerta = today
    lavoro.data_offerta_check = True
    lavoro.offerta_tipo = tipo
    if has_prev_offerta and dirty:
        lavoro.offerta_revision = rev_to_use
    lavoro.offerta_dirty = False
    db.session.commit()

    mesi = ["", "gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
    data_breve = f"{today.day:02d}-{mesi[today.month]}"

    def sanitize_filename(s: str) -> str:
        s = (s or "").strip()
        for ch in ['<', '>', ':', '\"', '/', '\\\\', '|', '?', '*']:
            s = s.replace(ch, ' ')
        s = " ".join(s.split())
        return s

    # Determina il suffisso del nome file in base al tipo
    if tipo == 'rsid':
        tipo_suffix = 'RSID'
    elif tipo == 'varie':
        tipo_suffix = 'VARIE'
    else:
        tipo_suffix = '4.0'  # Per "old" e "iper"
    
    base_name = f"Prev. First Eng_{sanitize_filename(cliente_nome)}_{tipo_suffix}"
    if rev_to_use > 0:
        base_name = f"{base_name} (Rev. {rev_to_use})"
    download_name = f"{base_name}.docx"

    resp = send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=download_name,
    )
    resp.headers["X-Offerta-Data-Breve"] = data_breve
    resp.headers["X-Offerta-Revision"] = str(rev_to_use)
    return resp

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
        # Di default mostra il totale degli importi (somma di tutte le celle importo_offerta)
        tot_importo = db.session.query(func.sum(LavoroAdmin.importo_offerta)).scalar() or 0
        
        # Totali compensi per ogni FE
        tot_fe = db.session.query(func.sum(LavoroAdmin.c_fe)).scalar() or 0
        tot_amin = db.session.query(func.sum(LavoroAdmin.c_amin)).scalar() or 0
        tot_galvan = db.session.query(func.sum(LavoroAdmin.c_galvan)).scalar() or 0
        tot_fh = db.session.query(func.sum(LavoroAdmin.c_fh)).scalar() or 0
        
        total_lavori = LavoroAdmin.query.count()
        in_corso = LavoroAdmin.query.filter(LavoroAdmin.stato.ilike('In corso')).count()
        completati = LavoroAdmin.query.filter(LavoroAdmin.stato.in_(['Fatturato', 'Completo', 'Chiuso'])).count()
        
        return render_template('main/dashboard.html',
                               role='admin',
                               tot_importo=tot_importo, tot_fe=tot_fe, tot_amin=tot_amin, tot_galvan=tot_galvan, tot_fh=tot_fh,
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
    
    # Carica i beni per ogni lavoro e crea una lista di dizionari per il template
    lavori_with_beni = []
    for lavoro in lavori:
        beni_list = []
        if lavoro.beni_list:
            # Usa i beni dalla tabella separata
            for bene in sorted(lavoro.beni_list, key=lambda x: x.ordine):
                beni_list.append({
                    'id': bene.id,
                    'descrizione': bene.descrizione,
                    'valore': bene.valore,
                    'importo_offerta': getattr(bene, 'importo_offerta', 0) or 0,
                    'stato': getattr(bene, 'stato', 'vuoto') or 'vuoto',
                    'data_pec': bene.data_pec
                })
        else:
            # Se non ci sono beni nella tabella separata, parsare dal campo concatenato
            if lavoro.bene and ' | ' in lavoro.bene:
                beni_parts = lavoro.bene.split(' | ')
                valore_per_bene = lavoro.valore_bene / len(beni_parts) if len(beni_parts) > 0 else lavoro.valore_bene
                importo_per_bene = lavoro.importo_offerta / len(beni_parts) if len(beni_parts) > 0 else lavoro.importo_offerta
                for desc in beni_parts:
                    beni_list.append({'descrizione': desc.strip(), 'valore': valore_per_bene, 'importo_offerta': importo_per_bene})
            else:
                # Un solo bene
                beni_list.append({'descrizione': lavoro.bene or '', 'valore': lavoro.valore_bene, 'importo_offerta': lavoro.importo_offerta})
        
        lavori_with_beni.append({'lavoro': lavoro, 'beni': beni_list})
    
    return render_template('main/lavori_admin.html', lavori_with_beni=lavori_with_beni, view_mode=view_mode)
    
# NUOVA ROTTA SPECIALE (Sostituto Firma - Solo per Extra 2)
@bp.route('/lavori_focus')
@login_required
def lavori_focus():
    if current_user.role != 'admin' or current_user.admin_view_mode != 'extra2':
        return redirect(url_for('main.dashboard'))
    
    lavori = LavoroAdmin.query.order_by(LavoroAdmin.numero.asc()).all()
    
    # Carica i beni per ogni lavoro e crea una lista di dizionari per il template
    lavori_with_beni = []
    for lavoro in lavori:
        beni_list = []
        if lavoro.beni_list:
            # Usa i beni dalla tabella separata
            for bene in sorted(lavoro.beni_list, key=lambda x: x.ordine):
                beni_list.append({
                    'id': bene.id,
                    'descrizione': bene.descrizione,
                    'valore': bene.valore,
                    'importo_offerta': getattr(bene, 'importo_offerta', 0) or 0,
                    'stato': getattr(bene, 'stato', 'vuoto') or 'vuoto',
                    'data_pec': bene.data_pec
                })
        else:
            # Se non ci sono beni nella tabella separata, parsare dal campo concatenato
            if lavoro.bene and ' | ' in lavoro.bene:
                beni_parts = lavoro.bene.split(' | ')
                valore_per_bene = lavoro.valore_bene / len(beni_parts) if len(beni_parts) > 0 else lavoro.valore_bene
                importo_per_bene = lavoro.importo_offerta / len(beni_parts) if len(beni_parts) > 0 else lavoro.importo_offerta
                for desc in beni_parts:
                    beni_list.append({'id': None, 'descrizione': desc.strip(), 'valore': valore_per_bene, 'importo_offerta': importo_per_bene, 'stato': lavoro.stato, 'data_pec': lavoro.data_pec})
            else:
                # Un solo bene
                beni_list.append({'id': None, 'descrizione': lavoro.bene or '', 'valore': lavoro.valore_bene, 'importo_offerta': lavoro.importo_offerta, 'stato': lavoro.stato, 'data_pec': lavoro.data_pec})
        
        lavori_with_beni.append({'lavoro': lavoro, 'beni': beni_list})
    
    return render_template('main/lavori_admin.html', lavori_with_beni=lavori_with_beni, view_mode='focus_special')

@bp.route('/api/lavoro/<int:id>', methods=['GET'])
@login_required
def get_lavoro_admin(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    lavoro = LavoroAdmin.query.get_or_404(id)
    
    # Debug: verifica valori letti dal database
    if lavoro.has_revisore:
        print(f"[DEBUG API] Revisore letto - tipo: {getattr(lavoro, 'rev_type', 'N/A')}, valore: {getattr(lavoro, 'rev_value', 'N/A')}")
    if lavoro.has_caricamento:
        print(f"[DEBUG API] Caricamento letto - tipo: {getattr(lavoro, 'car_type', 'N/A')}, valore: {getattr(lavoro, 'car_value', 'N/A')}")
    cliente = Cliente.query.get(lavoro.cliente_id) if lavoro.cliente_id else None
    
    # Recupera i beni
    beni_list = []
    if lavoro.beni_list:
        for bene in sorted(lavoro.beni_list, key=lambda x: x.ordine):
            beni_list.append({
                'id': bene.id,
                'descrizione': bene.descrizione,
                'valore': bene.valore,
                'importo_offerta': getattr(bene, 'importo_offerta', 0) or 0,
                'stato': getattr(bene, 'stato', 'vuoto') or 'vuoto',
                'data_pec': bene.data_pec.strftime('%Y-%m-%d') if getattr(bene, 'data_pec', None) else None
            })
    else:
        # Fallback: parsare dal campo concatenato
        if lavoro.bene and ' | ' in lavoro.bene:
            beni_parts = lavoro.bene.split(' | ')
            valore_per_bene = lavoro.valore_bene / len(beni_parts) if len(beni_parts) > 0 else lavoro.valore_bene
            importo_per_bene = lavoro.importo_offerta / len(beni_parts) if len(beni_parts) > 0 else lavoro.importo_offerta
            for desc in beni_parts:
                beni_list.append({'id': None, 'descrizione': desc.strip(), 'valore': valore_per_bene, 'importo_offerta': importo_per_bene, 'stato': lavoro.stato, 'data_pec': lavoro.data_pec.strftime('%Y-%m-%d') if lavoro.data_pec else None})
        else:
            beni_list.append({'id': None, 'descrizione': lavoro.bene or '', 'valore': lavoro.valore_bene, 'importo_offerta': lavoro.importo_offerta, 'stato': lavoro.stato, 'data_pec': lavoro.data_pec.strftime('%Y-%m-%d') if lavoro.data_pec else None})
    
    return jsonify({
        'id': lavoro.id,
        'numero': lavoro.numero,
        'cliente': {
            'nome': lavoro.cliente_nome,
            'p_iva': cliente.p_iva if cliente else '',
            'indirizzo': cliente.indirizzo if cliente else '',
            'civico': cliente.civico if cliente else '',
            'cap': cliente.cap if cliente else '',
            'comune': cliente.comune if cliente else '',
            'provincia': cliente.provincia if cliente else '',
            'pec': cliente.pec if cliente else ''
        },
        'beni': beni_list,
        'importo_offerta': lavoro.importo_offerta,
        'origine': lavoro.origine or '',
        'nome_esterno': lavoro.nome_esterno or '',
        'redattore': lavoro.redattore or '',
        'collaboratore': lavoro.collaboratore or '',
        'has_revisore': lavoro.has_revisore,
        'has_caricamento': lavoro.has_caricamento,
        'nome_revisore': lavoro.nome_revisore or '',
        'nome_caricamento': lavoro.nome_caricamento or '',
        'rev_type': getattr(lavoro, 'rev_type', 'perc') if lavoro.has_revisore else 'perc',
        'rev_value': float(getattr(lavoro, 'rev_value', 0)) if lavoro.has_revisore else 0,
        'car_type': getattr(lavoro, 'car_type', 'perc') if lavoro.has_caricamento else 'perc',
        'car_value': float(getattr(lavoro, 'car_value', 0)) if lavoro.has_caricamento else 0,
        'ext_type': getattr(lavoro, 'ext_type', 'perc') if lavoro.origine == 'ext' else 'perc',
        'ext_value': float(getattr(lavoro, 'ext_value', 0)) if lavoro.origine == 'ext' else 0,
        'importo_revisione': getattr(lavoro, 'importo_revisione', 0) if lavoro.has_revisore else 0,
        'importo_caricamento': getattr(lavoro, 'importo_caricamento', 0) if lavoro.has_caricamento else 0,
        'spese_amministrative': getattr(lavoro, 'spese_amministrative', False),
        'offerta_revision': getattr(lavoro, 'offerta_revision', 0),
        'offerta_dirty': getattr(lavoro, 'offerta_dirty', False),
        'offerta_tipo': getattr(lavoro, 'offerta_tipo', '') or '',
        'c_fe': lavoro.c_fe,
        'c_amin': lavoro.c_amin,
        'c_galvan': lavoro.c_galvan,
        'c_fh': lavoro.c_fh,
        'c_bianc': lavoro.c_bianc,
        'c_deloitte': getattr(lavoro, 'c_deloitte', 0.0),
        'c_ext': lavoro.c_ext,
        'c_revisore': lavoro.c_revisore,
        'c_caricamento': lavoro.c_caricamento,
        'data_offerta': lavoro.data_offerta.strftime('%Y-%m-%d') if lavoro.data_offerta else None,
        'data_firma': lavoro.data_firma.strftime('%Y-%m-%d') if lavoro.data_firma else None,
        'data_pec': lavoro.data_pec.strftime('%Y-%m-%d') if lavoro.data_pec else None,
        'firma_esito': getattr(lavoro, 'firma_esito', '') or '',
        'stato': lavoro.stato,
        'categoria': getattr(lavoro, 'categoria', '') or '',
        'f_fe': lavoro.f_fe or '',
        'f_amin': lavoro.f_amin or '',
        'f_galvan': lavoro.f_galvan or '',
        'f_fh': lavoro.f_fh or '',
        'f_bianc': lavoro.f_bianc or '',
        'f_deloitte': getattr(lavoro, 'f_deloitte', '') or '',
        'f_ext': lavoro.f_ext or '',
        'f_revisore': lavoro.f_revisore or '',
        'f_caricamento': lavoro.f_caricamento or ''
    })


@bp.route('/api/lavoro/<int:id>/genera_offerta', methods=['POST'])
@login_required
def genera_offerta(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lavoro = LavoroAdmin.query.get_or_404(id)
    cliente = Cliente.query.get(lavoro.cliente_id) if lavoro.cliente_id else None

    payload = request.get_json(silent=True) or {}
    tipo = (payload.get('tipo') or '').strip().lower()  # 'old' | 'iper' | 'rsid' | 'varie'
    
    # Se il tipo non è specificato, determinalo dalla categoria
    if not tipo:
        # Prima prova con offerta_tipo esistente (per retrocompatibilità)
        tipo = (getattr(lavoro, 'offerta_tipo', '') or '').strip().lower()
        
        # Se ancora non c'è, usa la categoria
        if not tipo:
            categoria = (getattr(lavoro, 'categoria', '') or '').strip().lower()
            if categoria == 'old':
                tipo = 'old'
            elif categoria == 'iperamm':
                tipo = 'iper'
            elif categoria == 'rsid':
                tipo = 'rsid'
            elif categoria == 'varie':
                tipo = 'varie'
    
    if tipo not in ('old', 'iper', 'rsid', 'varie'):
        return jsonify({'error': 'Tipo offerta non valido. Imposta una categoria al lavoro.'}), 400

    return _generate_offerta_response(lavoro=lavoro, tipo=tipo)

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
    
    # 2. VERIFICA SE È UN UPDATE O UN NUOVO LAVORO
    lavoro_id = request.form.get('lavoro_id')
    is_update = lavoro_id and lavoro_id.strip()
    
    if is_update:
        # UPDATE: recupera il lavoro esistente
        lavoro = LavoroAdmin.query.get_or_404(int(lavoro_id))
        new_num = lavoro.numero  # Mantieni lo stesso numero
        had_prev_offerta = bool(lavoro.data_offerta)
    else:
        # NUOVO: calcola il nuovo numero
        last = LavoroAdmin.query.order_by(LavoroAdmin.numero.desc()).first()
        new_num = (last.numero + 1) if (last and last.numero) else 1
        lavoro = None

    download_offerta = (request.args.get('download_offerta') == '1')

    # 3. CREAZIONE/AGGIORNAMENTO LAVORO
    try:
        # Helper per convertire float
        def to_float(val):
            try:
                if isinstance(val, str):
                    val = val.strip()
                    # Se contiene sia punto che virgola, assume formato italiano (1.234,56)
                    if '.' in val and ',' in val:
                        val = val.replace('.', '').replace(',', '.')
                    # Se contiene solo virgola, assume formato italiano (1170,75)
                    elif ',' in val:
                        val = val.replace(',', '.')
                    # Se contiene solo punto, assume formato internazionale (1170.75)
                    # (non fa nulla, il punto è già il separatore decimale)
                return float(val)
            except: 
                return 0.0

        # --- GESTIONE BENI MULTIPLI ---
        beni_data = []  # Lista di tuple (bene_id, descrizione, valore, importo_offerta)
        valore_totale_beni = 0.0
        importo_totale_offerta = 0.0
        
        # Itera sui beni inviati dal form (beni[0], beni[1], ecc.)
        i = 0
        while True:
            desc_key = f'beni[{i}][descrizione]'
            val_key = f'beni[{i}][valore]'
            imp_key = f'beni[{i}][importo_offerta]'
            id_key = f'beni[{i}][id]'
            
            # Se non esiste la chiave per l'indice corrente, interrompi il ciclo
            if desc_key not in request.form:
                break
                
            descrizione = request.form.get(desc_key, '').strip()
            valore_str = request.form.get(val_key, '0')
            importo_str = request.form.get(imp_key, '0')
            bene_id_str = request.form.get(id_key, '').strip()
            
            # Converti valori
            valore = to_float(valore_str)
            importo_offerta = to_float(importo_str)
            bene_id = int(bene_id_str) if bene_id_str.isdigit() else None
            
            if descrizione:
                beni_data.append((bene_id, descrizione, valore, importo_offerta))
                valore_totale_beni += valore
                importo_totale_offerta += importo_offerta
                
            i += 1

        # Genera stringa concatenata per retrocompatibilità (es. "Appartamento A | Box Auto")
        if beni_data:
            # beni_data: (bene_id, descrizione, valore, importo_offerta)
            bene_concatenato = ' | '.join([b[1] for b in beni_data])
        else:
            bene_concatenato = request.form.get('bene', '') # Fallback

        # Se il valore totale calcolato è 0, controlla se c'è un valore singolo inserito (fallback)
        if valore_totale_beni == 0.0 and request.form.get('valore_bene'):
            valore_totale_beni = to_float(request.form.get('valore_bene'))

        if is_update:
            # AGGIORNA LAVORO ESISTENTE
            lavoro.numero = new_num
            lavoro.cliente_id = cliente.id
            lavoro.cliente_nome = nome_cliente
            lavoro.bene = bene_concatenato
            lavoro.valore_bene = valore_totale_beni
            lavoro.importo_offerta = to_float(request.form.get('importo_offerta'))
            lavoro.origine = request.form.get('origine')
            lavoro.nome_esterno = request.form.get('nome_esterno')
            lavoro.redattore = request.form.get('redattore')
            lavoro.collaboratore = request.form.get('collaboratore')
            lavoro.has_revisore = (request.form.get('has_revisore') == 'on')
            lavoro.has_caricamento = (request.form.get('has_caricamento') == 'on')
            lavoro.spese_amministrative = (request.form.get('spese_amministrative') == 'on')
            
            # Gestione cambio categoria
            nuova_categoria = request.form.get('categoria') or None
            vecchia_categoria = getattr(lavoro, 'categoria', '') or ''
            categoria_cambiata = vecchia_categoria != nuova_categoria
            
            if categoria_cambiata and nuova_categoria:
                # Se la categoria è cambiata, aggiorna offerta_tipo in base alla nuova categoria
                if nuova_categoria == 'old':
                    lavoro.offerta_tipo = 'old'
                elif nuova_categoria == 'iperamm':
                    lavoro.offerta_tipo = 'iper'
                elif nuova_categoria == 'rsid':
                    lavoro.offerta_tipo = 'rsid'
                elif nuova_categoria == 'varie':
                    lavoro.offerta_tipo = 'varie'
                
                # Se c'era già un'offerta e la categoria è cambiata, marca come da revisionare
                if had_prev_offerta:
                    lavoro.offerta_dirty = True
            
            lavoro.categoria = nuova_categoria
            
            # Qualsiasi salvataggio dopo emissione offerta rende l'offerta "da revisionare"
            # (ma solo se la categoria non è cambiata, altrimenti l'abbiamo già gestito sopra)
            if had_prev_offerta and not categoria_cambiata:
                lavoro.offerta_dirty = True
            lavoro.nome_revisore = request.form.get('nome_revisore') if lavoro.has_revisore else None
            lavoro.nome_caricamento = request.form.get('nome_caricamento') if lavoro.has_caricamento else None
            
            # Salva valori originali revisore e caricamento
            if lavoro.has_revisore:
                rev_type_val = request.form.get('rev_type', 'perc')
                rev_val_val = to_float(request.form.get('rev_val', '0'))
                lavoro.rev_type = rev_type_val
                lavoro.rev_value = rev_val_val
                print(f"[DEBUG UPDATE] Revisore salvato - tipo: {rev_type_val}, valore: {rev_val_val}")
            else:
                lavoro.rev_type = 'perc'
                lavoro.rev_value = 0.0
                
            if lavoro.has_caricamento:
                car_type_val = request.form.get('car_type', 'perc')
                car_val_val = to_float(request.form.get('car_val', '0'))
                lavoro.car_type = car_type_val
                lavoro.car_value = car_val_val
                print(f"[DEBUG UPDATE] Caricamento salvato - tipo: {car_type_val}, valore: {car_val_val}")
            else:
                lavoro.car_type = 'perc'
                lavoro.car_value = 0.0
            
            # Salva valori originali esterno
            if lavoro.origine == 'ext':
                ext_type_val = request.form.get('ext_type', 'perc')
                ext_val_val = to_float(request.form.get('ext_val', '0'))
                lavoro.ext_type = ext_type_val
                lavoro.ext_value = ext_val_val
                print(f"[DEBUG UPDATE] Esterno salvato - tipo: {ext_type_val}, valore: {ext_val_val}")
            else:
                lavoro.ext_type = 'perc'
                lavoro.ext_value = 0.0
            
            lavoro.c_fe = to_float(request.form.get('c_fe'))
            lavoro.c_amin = to_float(request.form.get('c_amin'))
            lavoro.c_galvan = to_float(request.form.get('c_galvan'))
            lavoro.c_fh = to_float(request.form.get('c_fh'))
            lavoro.c_bianc = to_float(request.form.get('c_bianc'))
            lavoro.c_deloitte = to_float(request.form.get('c_deloitte'))
            lavoro.c_ext = to_float(request.form.get('c_ext'))
            lavoro.c_revisore = to_float(request.form.get('c_revisore'))
            lavoro.c_caricamento = to_float(request.form.get('c_caricamento'))
            
            # Salva gli importi per l'offerta al cliente (sezione Ordine di Lavoro)
            lavoro.importo_revisione = to_float(request.form.get('importo_revisione', '0'))
            lavoro.importo_caricamento = to_float(request.form.get('importo_caricamento', '0'))
            
            # Aggiorna importo_offerta totale
            lavoro.importo_offerta = importo_totale_offerta
            
            # Upsert beni: mantiene gli ID e quindi stato/data_pec per bene
            existing = {b.id: b for b in lavoro.beni_list}
            seen_ids = set()

            for ordine, (bene_id, descrizione, valore, importo_off) in enumerate(beni_data):
                if bene_id and bene_id in existing:
                    b = existing[bene_id]
                    b.descrizione = descrizione
                    b.valore = valore
                    b.importo_offerta = importo_off
                    b.ordine = ordine
                    seen_ids.add(bene_id)
                else:
                    b = Bene(
                        lavoro_id=lavoro.id,
                        descrizione=descrizione,
                        valore=valore,
                        importo_offerta=importo_off,
                        ordine=ordine
                    )
                    db.session.add(b)

            # Elimina beni rimossi
            for b in lavoro.beni_list:
                if b.id not in seen_ids and b.id in existing:
                    db.session.delete(b)
            
            db.session.commit()
            
            # Debug: verifica valori salvati dopo update
            lavoro_refreshed = LavoroAdmin.query.get(lavoro.id)
            if lavoro_refreshed.has_revisore:
                print(f"[DEBUG UPDATE] Revisore verificato dopo commit - tipo: {lavoro_refreshed.rev_type}, valore: {lavoro_refreshed.rev_value}")
            if lavoro_refreshed.has_caricamento:
                print(f"[DEBUG UPDATE] Caricamento verificato dopo commit - tipo: {lavoro_refreshed.car_type}, valore: {lavoro_refreshed.car_value}")
            
            # Se richiesto, genera e scarica subito la revisione offerta (senza passare dal menu "Modifica")
            if download_offerta:
                # Determina il tipo: prima da querystring, poi da offerta_tipo, infine dalla categoria
                tipo = (request.args.get('tipo') or '').strip().lower()
                if not tipo:
                    tipo = (getattr(lavoro, 'offerta_tipo', '') or '').strip().lower()
                if not tipo:
                    # Usa la categoria per determinare il tipo
                    categoria = (getattr(lavoro, 'categoria', '') or '').strip().lower()
                    if categoria == 'old':
                        tipo = 'old'
                    elif categoria == 'iperamm':
                        tipo = 'iper'
                    elif categoria == 'rsid':
                        tipo = 'rsid'
                    elif categoria == 'varie':
                        tipo = 'varie'
                
                if tipo not in ('old', 'iper', 'rsid', 'varie'):
                    return jsonify({'error': 'Tipo offerta non impostato. Imposta una categoria al lavoro.'}), 400
                return _generate_offerta_response(lavoro=lavoro, tipo=tipo)

            flash(f'Lavoro #{lavoro.numero} modificato con successo!', 'success')
        else:
            # CREA NUOVO LAVORO
            nuovo = LavoroAdmin(
                numero=new_num,
                cliente_id=cliente.id,
                cliente_nome=nome_cliente,
                bene=bene_concatenato, 
                valore_bene=valore_totale_beni,
                importo_offerta=importo_totale_offerta,
                origine=request.form.get('origine'),
                nome_esterno=request.form.get('nome_esterno'),
                redattore=request.form.get('redattore'),
                collaboratore=request.form.get('collaboratore'),
                has_revisore=(request.form.get('has_revisore') == 'on'),
                has_caricamento=(request.form.get('has_caricamento') == 'on'),
                spese_amministrative=(request.form.get('spese_amministrative') == 'on'),
                nome_revisore=request.form.get('nome_revisore') if (request.form.get('has_revisore') == 'on') else None,
                nome_caricamento=request.form.get('nome_caricamento') if (request.form.get('has_caricamento') == 'on') else None,
                rev_type=request.form.get('rev_type', 'perc') if (request.form.get('has_revisore') == 'on') else 'perc',
                rev_value=to_float(request.form.get('rev_val', '0')) if (request.form.get('has_revisore') == 'on') else 0.0,
                car_type=request.form.get('car_type', 'perc') if (request.form.get('has_caricamento') == 'on') else 'perc',
                car_value=to_float(request.form.get('car_val', '0')) if (request.form.get('has_caricamento') == 'on') else 0.0,
                c_fe=to_float(request.form.get('c_fe')),
                c_amin=to_float(request.form.get('c_amin')),
                c_galvan=to_float(request.form.get('c_galvan')),
                c_fh=to_float(request.form.get('c_fh')),
                c_bianc=to_float(request.form.get('c_bianc')),
                c_deloitte=to_float(request.form.get('c_deloitte')),
                c_ext=to_float(request.form.get('c_ext')),
                c_revisore=to_float(request.form.get('c_revisore')),
                c_caricamento=to_float(request.form.get('c_caricamento')),
                importo_revisione=to_float(request.form.get('importo_revisione', '0')),
                importo_caricamento=to_float(request.form.get('importo_caricamento', '0')),
                categoria=request.form.get('categoria') or None,
                stato='In corso' # Default
            )
            
            # Imposta offerta_tipo in base alla categoria per i nuovi lavori
            if nuovo.categoria:
                if nuovo.categoria == 'old':
                    nuovo.offerta_tipo = 'old'
                elif nuovo.categoria == 'iperamm':
                    nuovo.offerta_tipo = 'iper'
                elif nuovo.categoria == 'rsid':
                    nuovo.offerta_tipo = 'rsid'
                elif nuovo.categoria == 'varie':
                    nuovo.offerta_tipo = 'varie'
            
            # Debug: verifica valori prima di salvare
            has_rev = (request.form.get('has_revisore') == 'on')
            has_car = (request.form.get('has_caricamento') == 'on')
            if has_rev:
                rev_t = request.form.get('rev_type', 'perc')
                rev_v = to_float(request.form.get('rev_val', '0'))
                print(f"[DEBUG CREATE] Revisore da salvare - tipo: {rev_t}, valore: {rev_v}")
            if has_car:
                car_t = request.form.get('car_type', 'perc')
                car_v = to_float(request.form.get('car_val', '0'))
                print(f"[DEBUG CREATE] Caricamento da salvare - tipo: {car_t}, valore: {car_v}")
            
            db.session.add(nuovo)
            db.session.flush()  # Per avere l'ID del lavoro

            # Salva i beni come record separati
            for ordine, (_bene_id, descrizione, valore, importo_off) in enumerate(beni_data):
                bene = Bene(
                    lavoro_id=nuovo.id,
                    descrizione=descrizione,
                    valore=valore,
                    importo_offerta=importo_off,
                    ordine=ordine
                )
                db.session.add(bene)
            
            db.session.commit()
            
            # Debug: verifica valori salvati dopo commit
            nuovo_refreshed = LavoroAdmin.query.get(nuovo.id)
            if nuovo_refreshed.has_revisore:
                print(f"[DEBUG CREATE] Revisore verificato dopo commit - tipo: {nuovo_refreshed.rev_type}, valore: {nuovo_refreshed.rev_value}")
            if nuovo_refreshed.has_caricamento:
                print(f"[DEBUG CREATE] Caricamento verificato dopo commit - tipo: {nuovo_refreshed.car_type}, valore: {nuovo_refreshed.car_value}")
            
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
    elif field == 'offerta_revision':
        lavoro.offerta_revision = int(value) if value is not None else 0
    elif field == 'data_firma_check':
        lavoro.data_firma_check = value
    elif field == 'data_firma':
        if value:
            lavoro.data_firma = datetime.strptime(value, '%Y-%m-%d').date()
            lavoro.data_firma_check = True
        else:
            lavoro.data_firma = None
            lavoro.data_firma_check = False
        lavoro.firma_esito = None
    elif field == 'firma_esito':
        # 'OK' | 'AUTORIZZ.' | '' (svuota)
        val = (value or '').strip()
        lavoro.firma_esito = val if val else None
        if lavoro.firma_esito:
            lavoro.data_firma = None
            lavoro.data_firma_check = False
    elif field == 'data_pec':
        if value: lavoro.data_pec = datetime.strptime(value, '%Y-%m-%d').date()
    
    # Eventuale gestione altri campi inline...

    db.session.commit()
    return jsonify({'success': True})


@bp.route('/update_bene_field/<int:id>', methods=['POST'])
@login_required
def update_bene_field(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    bene = Bene.query.get_or_404(id)
    data = request.json or {}
    field = data.get('field')
    value = data.get('value')

    if field == 'stato':
        bene.stato = value or 'vuoto'
    elif field == 'data_pec':
        if value:
            bene.data_pec = datetime.strptime(value, '%Y-%m-%d').date()
        else:
            bene.data_pec = None
    else:
        return jsonify({'error': 'Campo non supportato'}), 400

    # Se l'offerta è già stata generata, qualsiasi modifica post-emissione rende l'offerta "da revisionare"
    try:
        lavoro = bene.lavoro
        if lavoro and getattr(lavoro, 'data_offerta', None):
            lavoro.offerta_dirty = True
    except Exception:
        pass

    db.session.commit()
    return jsonify({'success': True})
    

@bp.route('/update_fattura/<int:id>', methods=['POST'])
@login_required
def update_fattura(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    lavoro = LavoroAdmin.query.get_or_404(id)
    data = request.json
    fattura_type = data.get('fattura_type')
    value = data.get('value')
    
    # Mappa il tipo di fattura al campo del modello
    fattura_field_map = {
        'fe': 'f_fe',
        'amin': 'f_amin',
        'galvan': 'f_galvan',
        'fh': 'f_fh',
        'bianc': 'f_bianc',
        'deloitte': 'f_deloitte',
        'ext': 'f_ext',
        'revisore': 'f_revisore',
        'caricamento': 'f_caricamento'
    }
    
    if fattura_type not in fattura_field_map:
        return jsonify({'error': 'Tipo fattura non supportato'}), 400
    
    field_name = fattura_field_map[fattura_type]
    setattr(lavoro, field_name, value)
    
    db.session.commit()
    return jsonify({'success': True})
    
@bp.route('/delete_lavoro_admin/<int:id>', methods=['POST'])
@login_required
def delete_lavoro_admin(id):
    if current_user.role != 'admin':
        flash('Accesso negato.', 'error')
        return redirect(url_for('main.dashboard'))
    
    lavoro = LavoroAdmin.query.get_or_404(id)
    
    # Elimina i beni associati al lavoro
    for bene in lavoro.beni_list:
        db.session.delete(bene)
    
    # Elimina il lavoro
    db.session.delete(lavoro)
    db.session.commit()
    
    # Rinumerazione sequenziale di tutti i lavori rimanenti
    lavori_rimanenti = LavoroAdmin.query.order_by(LavoroAdmin.numero.asc()).all()
    for idx, lav in enumerate(lavori_rimanenti, start=1):
        lav.numero = idx
    
    db.session.commit()
    
    flash(f'Lavoro #{id} eliminato con successo. Numerazione aggiornata.', 'success')
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

@bp.route('/api/revisori')
@login_required
def api_revisori():
    query = request.args.get('q', '')
    if len(query) < 1:
        return jsonify([])
    
    # Cerca i nomi univoci nella colonna nome_revisore
    nomi = db.session.query(LavoroAdmin.nome_revisore)\
        .filter(LavoroAdmin.nome_revisore.ilike(f'%{query}%'))\
        .filter(LavoroAdmin.nome_revisore != None)\
        .filter(LavoroAdmin.nome_revisore != '')\
        .distinct().limit(10).all()
    
    results = [n[0] for n in nomi]
    return jsonify(results)

@bp.route('/api/caricamenti')
@login_required
def api_caricamenti():
    query = request.args.get('q', '')
    if len(query) < 1:
        return jsonify([])
    
    # Cerca i nomi univoci nella colonna nome_caricamento
    nomi = db.session.query(LavoroAdmin.nome_caricamento)\
        .filter(LavoroAdmin.nome_caricamento.ilike(f'%{query}%'))\
        .filter(LavoroAdmin.nome_caricamento != None)\
        .filter(LavoroAdmin.nome_caricamento != '')\
        .distinct().limit(10).all()
    
    results = [n[0] for n in nomi]
    return jsonify(results)