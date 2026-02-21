#!/usr/bin/env python3
"""
Script per inserire lavori di test nel database.
Eseguire con: python init_test_lavori.py

Su PythonAnywhere:
1. Vai nella Console Bash
2. Naviga nella directory del progetto
3. Esegui: python3.10 init_test_lavori.py (o la versione Python che usi)
"""
from app import create_app, db
from app.models import Cliente, LavoroAdmin, Bene, Lavoro40, Lavoro50
from datetime import date, datetime, timedelta

app = create_app()

def init_test_lavori():
    with app.app_context():
        print("=== Inserimento Lavori di Test ===\n")
        
        # 1. Crea clienti di test
        print("1. Creazione clienti di test...")
        clienti_test = [
            {
                'nome': 'Azienda Test S.r.l.',
                'p_iva': 'IT12345678901',
                'indirizzo': 'Via Roma',
                'civico': '10',
                'cap': '00100',
                'comune': 'Roma',
                'provincia': 'RM',
                'pec': 'test@pec.it'
            },
            {
                'nome': 'Impresa Demo S.p.A.',
                'p_iva': 'IT98765432109',
                'indirizzo': 'Via Milano',
                'civico': '25',
                'cap': '20100',
                'comune': 'Milano',
                'provincia': 'MI',
                'pec': 'demo@pec.it'
            },
            {
                'nome': 'Studio Legale Test',
                'p_iva': 'IT11223344556',
                'indirizzo': 'Corso Vittorio Emanuele',
                'civico': '50',
                'cap': '10121',
                'comune': 'Torino',
                'provincia': 'TO',
                'pec': 'studio@pec.it'
            }
        ]
        
        clienti_creati = {}
        for cliente_data in clienti_test:
            nome = cliente_data['nome']
            cliente = Cliente.query.filter_by(nome=nome).first()
            
            if not cliente:
                cliente = Cliente(**cliente_data)
                db.session.add(cliente)
                db.session.flush()
                print(f"  [OK] Cliente '{nome}' creato (ID: {cliente.id})")
            else:
                print(f"  [OK] Cliente '{nome}' già esistente (ID: {cliente.id})")
            
            clienti_creati[nome] = cliente
        
        db.session.commit()
        print()
        
        # 2. Crea lavori Admin di test con diverse categorie e stati
        print("2. Creazione lavori Admin di test...")
        
        # Calcola il prossimo numero disponibile
        last_lavoro = LavoroAdmin.query.order_by(LavoroAdmin.numero.desc()).first()
        next_num = (last_lavoro.numero + 1) if last_lavoro and last_lavoro.numero else 1
        
        lavori_test = [
            {
                'numero': next_num,
                'cliente_id': clienti_creati['Azienda Test S.r.l.'].id,
                'cliente_nome': 'Azienda Test S.r.l.',
                'bene': 'Immobile residenziale - Via Roma 10',
                'valore_bene': 250000.0,
                'importo_offerta': 5000.0,
                'categoria': 'old',
                'offerta_tipo': 'old',
                'stato': 'In corso',
                'origine': 'AMIN',
                'redattore': 'AMIN',
                'data_offerta_check': True,
                'data_offerta': date.today() - timedelta(days=10),
                'has_revisore': True,
                'rev_type': 'perc',
                'rev_value': 10.0,
                'importo_revisione': 500.0,
                'beni': [
                    {'descrizione': 'Immobile residenziale - Via Roma 10', 'valore': 250000.0, 'importo_offerta': 5000.0}
                ]
            },
            {
                'numero': next_num + 1,
                'cliente_id': clienti_creati['Impresa Demo S.p.A.'].id,
                'cliente_nome': 'Impresa Demo S.p.A.',
                'bene': 'Capannone industriale - Via Milano 25',
                'valore_bene': 500000.0,
                'importo_offerta': 8000.0,
                'categoria': 'iperamm',
                'offerta_tipo': 'iper',
                'stato': 'Firmato',
                'origine': 'GALVAN',
                'redattore': 'GALVAN',
                'data_offerta_check': True,
                'data_offerta': date.today() - timedelta(days=20),
                'data_firma_check': True,
                'data_firma': date.today() - timedelta(days=5),
                'firma_esito': 'OK',
                'has_caricamento': True,
                'car_type': 'euro',
                'car_value': 200.0,
                'importo_caricamento': 200.0,
                'beni': [
                    {'descrizione': 'Capannone industriale - Via Milano 25', 'valore': 500000.0, 'importo_offerta': 8000.0}
                ]
            },
            {
                'numero': next_num + 2,
                'cliente_id': clienti_creati['Studio Legale Test'].id,
                'cliente_nome': 'Studio Legale Test',
                'bene': 'Uffici commerciali - Corso Vittorio Emanuele 50',
                'valore_bene': 350000.0,
                'importo_offerta': 6000.0,
                'categoria': 'rsid',
                'offerta_tipo': 'rsid',
                'stato': 'In corso',
                'origine': 'FH',
                'redattore': 'AMIN',
                'collaboratore': 'Gianmarco',
                'data_offerta_check': False,
                'has_revisore': True,
                'has_caricamento': True,
                'rev_type': 'perc',
                'rev_value': 15.0,
                'car_type': 'perc',
                'car_value': 5.0,
                'beni': [
                    {'descrizione': 'Uffici commerciali - Piano terra', 'valore': 200000.0, 'importo_offerta': 3500.0},
                    {'descrizione': 'Uffici commerciali - Primo piano', 'valore': 150000.0, 'importo_offerta': 2500.0}
                ]
            },
            {
                'numero': next_num + 3,
                'cliente_id': clienti_creati['Azienda Test S.r.l.'].id,
                'cliente_nome': 'Azienda Test S.r.l.',
                'bene': 'Terreno edificabile - Zona periferica',
                'valore_bene': 180000.0,
                'importo_offerta': 4000.0,
                'categoria': 'varie',
                'offerta_tipo': 'varie',
                'stato': 'Abbandonato',
                'origine': 'ext',
                'redattore': 'GALVAN',
                'nome_esterno': 'Studio Esterno Test',
                'data_offerta_check': True,
                'data_offerta': date.today() - timedelta(days=30),
                'beni': [
                    {'descrizione': 'Terreno edificabile - 1000 mq', 'valore': 180000.0, 'importo_offerta': 4000.0}
                ]
            },
            {
                'numero': next_num + 4,
                'cliente_id': clienti_creati['Impresa Demo S.p.A.'].id,
                'cliente_nome': 'Impresa Demo S.p.A.',
                'bene': 'Magazzino - Zona industriale',
                'valore_bene': 120000.0,
                'importo_offerta': 3000.0,
                'categoria': 'old',
                'offerta_tipo': 'old',
                'stato': 'vuoto',
                'origine': 'FH',
                'redattore': 'GALVAN',
                'beni': [
                    {'descrizione': 'Magazzino - 500 mq', 'valore': 120000.0, 'importo_offerta': 3000.0}
                ]
            }
        ]
        
        for lavoro_data in lavori_test:
            beni_data = lavoro_data.pop('beni', [])
            
            lavoro = LavoroAdmin(**lavoro_data)
            db.session.add(lavoro)
            db.session.flush()
            
            print(f"  [OK] Lavoro #{lavoro.numero} creato (ID: {lavoro.id}) - {lavoro.cliente_nome} - {lavoro.categoria}")
            
            # Aggiungi i beni associati
            for idx, bene_data in enumerate(beni_data):
                bene = Bene(
                    lavoro_id=lavoro.id,
                    descrizione=bene_data['descrizione'],
                    valore=bene_data['valore'],
                    importo_offerta=bene_data['importo_offerta'],
                    ordine=idx
                )
                db.session.add(bene)
            
            db.session.flush()
        
        db.session.commit()
        print()
        
        # 3. Crea lavori 40 di test
        print("3. Creazione lavori 40 di test...")
        last_40 = Lavoro40.query.order_by(Lavoro40.numero.desc()).first()
        next_num_40 = (last_40.numero + 1) if last_40 and last_40.numero else 1
        
        lavori_40_test = [
            {
                'numero': next_num_40,
                'cliente': 'Cliente Test 40-1',
                'bene': 'Immobile residenziale',
                'contattato': True,
                'data_contatto': date.today() - timedelta(days=5),
                'note': 'Primo contatto effettuato, cliente interessato',
                'esito': 'In attesa',
                'sollecito': False
            },
            {
                'numero': next_num_40 + 1,
                'cliente': 'Cliente Test 40-2',
                'bene': 'Uffici',
                'contattato': False,
                'data_contatto': None,
                'note': 'Da contattare',
                'esito': None,
                'sollecito': False
            }
        ]
        
        for lavoro_data in lavori_40_test:
            lavoro = Lavoro40(**lavoro_data)
            db.session.add(lavoro)
            print(f"  [OK] Lavoro 40 #{lavoro.numero} creato (ID: {lavoro.id})")
        
        db.session.commit()
        print()
        
        # 4. Crea lavori 50 di test
        print("4. Creazione lavori 50 di test...")
        last_50 = Lavoro50.query.order_by(Lavoro50.numero.desc()).first()
        next_num_50 = (last_50.numero + 1) if last_50 and last_50.numero else 1
        
        lavori_50_test = [
            {
                'numero': next_num_50,
                'cliente': 'Cliente Test 50-1',
                'bene': 'Capannone industriale',
                'contattato': True,
                'data_contatto': date.today() - timedelta(days=3),
                'note': 'Valutazione in corso',
                'codice': 'TEST001'
            },
            {
                'numero': next_num_50 + 1,
                'cliente': 'Cliente Test 50-2',
                'bene': 'Terreno',
                'contattato': False,
                'data_contatto': None,
                'note': 'In attesa di documentazione',
                'codice': 'TEST002'
            }
        ]
        
        for lavoro_data in lavori_50_test:
            lavoro = Lavoro50(**lavoro_data)
            db.session.add(lavoro)
            print(f"  [OK] Lavoro 50 #{lavoro.numero} creato (ID: {lavoro.id})")
        
        db.session.commit()
        print()
        
        # Riepilogo
        print("=== Riepilogo Lavori di Test ===")
        total_admin = LavoroAdmin.query.count()
        total_40 = Lavoro40.query.count()
        total_50 = Lavoro50.query.count()
        total_beni = Bene.query.count()
        
        print(f"  Lavori Admin: {total_admin}")
        print(f"  Lavori 40: {total_40}")
        print(f"  Lavori 50: {total_50}")
        print(f"  Beni totali: {total_beni}")
        print(f"  Clienti: {Cliente.query.count()}")
        print("\n[OK] Inserimento lavori di test completato!")
        print("\nI lavori creati includono:")
        print("  - Diverse categorie (old, iperamm, rsid, varie)")
        print("  - Diversi stati (In corso, Firmato, Abbandonato, vuoto)")
        print("  - Lavori con e senza revisore/caricamento")
        print("  - Lavori con più beni associati")
        print("  - Lavori 40 e 50 per test completi")

if __name__ == '__main__':
    init_test_lavori()
