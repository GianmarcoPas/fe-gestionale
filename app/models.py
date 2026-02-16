from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- MODELLO UTENTE ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='base')
    admin_view_mode = db.Column(db.String(20), default='extra2')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- ANAGRAFICA CLIENTI ---
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), unique=True)
    p_iva = db.Column(db.String(50))
    indirizzo = db.Column(db.String(150))
    civico = db.Column(db.String(20))
    cap = db.Column(db.String(10))
    comune = db.Column(db.String(100))
    provincia = db.Column(db.String(5))
    pec = db.Column(db.String(100))

# --- BENI (Tabella separata per beni multipli) ---
class Bene(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lavoro_id = db.Column(db.Integer, db.ForeignKey('lavoro_admin.id'), nullable=False)
    descrizione = db.Column(db.Text, nullable=False)
    valore = db.Column(db.Float, default=0.0)
    importo_offerta = db.Column(db.Float, default=0.0)  # Importo offerta per questo bene
    stato = db.Column(db.String(50), default='vuoto')  # Stato per bene
    data_pec = db.Column(db.Date, nullable=True)  # Data PEC per bene
    ordine = db.Column(db.Integer, default=0)  # Per mantenere l'ordine di inserimento
    motivo_abbandono = db.Column(db.String(100), nullable=True)  # Motivo abbandono: 'assegnato_altro_studio', 'abbandonato_cliente', 'altro'
    commento_abbandono = db.Column(db.Text, nullable=True)  # Commento quando motivo_abbandono è 'altro'
    data_abbandono = db.Column(db.Date, nullable=True)  # Data in cui il bene è stato abbandonato
    ordine_abbandono = db.Column(db.Integer, nullable=True)  # Ordine progressivo globale di abbandono
    
    lavoro = db.relationship('LavoroAdmin', backref='beni_list')

# --- LAVORI ADMIN (NUOVO) ---
class LavoroAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer) 
    
    # Anagrafica
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    cliente_rel = db.relationship('Cliente', backref='lavori')
    cliente_nome = db.Column(db.String(150)) 

    # Ordine di Lavoro (mantenuto per retrocompatibilità)
    bene = db.Column(db.Text)
    valore_bene = db.Column(db.Float, default=0.0)
    importo_offerta = db.Column(db.Float, default=0.0)
    origine = db.Column(db.String(50)) 
    nome_esterno = db.Column(db.String(100))
    redattore = db.Column(db.String(50))
    collaboratore = db.Column(db.String(100)) 

    # Date e Checkbox
    data_offerta_check = db.Column(db.Boolean, default=False)
    data_offerta = db.Column(db.Date, nullable=True)
    data_firma_check = db.Column(db.Boolean, default=False)
    data_firma = db.Column(db.Date, nullable=True)
    data_pec = db.Column(db.Date, nullable=True)
    firma_esito = db.Column(db.String(20))  # 'OK' | 'AUTORIZZ.' oppure None
    
    # Campi per utenti base
    data_contatto = db.Column(db.Date, nullable=True)
    note = db.Column(db.Text)
    sollecito = db.Column(db.Boolean, default=False)
    data_sollecito = db.Column(db.Date, nullable=True)
    compenso = db.Column(db.Float, default=0.0)  # Compenso assegnato da Roberto all'utente base
    
    # Stato
    stato = db.Column(db.String(50), default='vuoto') 
    
    # Categoria lavoro
    categoria = db.Column(db.String(20))  # 'old', 'iperamm', 'rsid', 'varie'

    # Offerte: revisione e "dirty" dopo modifiche
    offerta_revision = db.Column(db.Integer, default=0)  # 0 = prima emissione (senza rev.)
    offerta_dirty = db.Column(db.Boolean, default=False)  # True se il lavoro è stato modificato dopo l'ultima offerta
    offerta_tipo = db.Column(db.String(10))  # 'old' | 'iper'

    # Checkbox Ruoli
    has_revisore = db.Column(db.Boolean, default=False)
    has_caricamento = db.Column(db.Boolean, default=False)

    # Spese amministrative (flag salvato a DB)
    spese_amministrative = db.Column(db.Boolean, default=False)
    
    # Nomi revisore e caricamento
    nome_revisore = db.Column(db.String(100))
    nome_caricamento = db.Column(db.String(100))
    
    # Importi per offerta al cliente (sezione Ordine di Lavoro)
    importo_revisione = db.Column(db.Float, default=0.0)  # Importo nell'offerta
    importo_caricamento = db.Column(db.Float, default=0.0)  # Importo nell'offerta
    
    # Valori originali per revisore, caricamento e esterno (per modifica - sezione Compensi)
    rev_type = db.Column(db.String(10), default='perc')  # 'perc' o 'euro'
    rev_value = db.Column(db.Float, default=0.0)  # Valore originale inserito
    car_type = db.Column(db.String(10), default='perc')  # 'perc' o 'euro'
    car_value = db.Column(db.Float, default=0.0)  # Valore originale inserito
    ext_type = db.Column(db.String(10), default='perc')  # 'perc' o 'euro'
    ext_value = db.Column(db.Float, default=0.0)  # Valore originale inserito

    # Compensi
    c_fe = db.Column(db.Float, default=0.0)
    c_amin = db.Column(db.Float, default=0.0)
    c_galvan = db.Column(db.Float, default=0.0)
    c_fh = db.Column(db.Float, default=0.0)
    c_bianc = db.Column(db.Float, default=0.0)
    c_deloitte = db.Column(db.Float, default=0.0)
    c_ext = db.Column(db.Float, default=0.0)
    c_revisore = db.Column(db.Float, default=0.0)
    c_caricamento = db.Column(db.Float, default=0.0)

    # Fatture (Placeholder stringhe per numeri fattura)
    f_fe = db.Column(db.String(50))
    f_amin = db.Column(db.String(50))
    f_galvan = db.Column(db.String(50))
    f_fh = db.Column(db.String(50))
    f_bianc = db.Column(db.String(50))
    f_deloitte = db.Column(db.String(50))
    f_ext = db.Column(db.String(50))
    f_revisore = db.Column(db.String(50))
    f_caricamento = db.Column(db.String(50))
    
    # Date fatturazione
    data_fattura_fe = db.Column(db.Date, nullable=True)
    data_fattura_amin = db.Column(db.Date, nullable=True)
    data_fattura_galvan = db.Column(db.Date, nullable=True)
    data_fattura_fh = db.Column(db.Date, nullable=True)
    data_fattura_bianc = db.Column(db.Date, nullable=True)
    data_fattura_deloitte = db.Column(db.Date, nullable=True)
    data_fattura_ext = db.Column(db.Date, nullable=True)
    data_fattura_revisore = db.Column(db.Date, nullable=True)
    data_fattura_caricamento = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- LAVORI BASE (LEGACY) ---
# Manteniamo questi per far funzionare la dashboard base
class Lavoro40(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    cliente = db.Column(db.String(100))
    bene = db.Column(db.String(200))
    contattato = db.Column(db.Boolean, default=False)
    data_contatto = db.Column(db.Date, nullable=True)
    note = db.Column(db.Text)
    esito = db.Column(db.String(50))
    sollecito = db.Column(db.Boolean, default=False)
    compenso = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lavoro50(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    cliente = db.Column(db.String(100))
    bene = db.Column(db.String(200))
    contattato = db.Column(db.Boolean, default=False)
    data_contatto = db.Column(db.Date, nullable=True)
    note = db.Column(db.Text)
    codice = db.Column(db.String(50))
    ex_ante = db.Column(db.String(20))
    perc_20 = db.Column(db.Boolean, default=False)
    ex_post = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)