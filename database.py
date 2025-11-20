import sqlite3
from datetime import datetime, timedelta
import uuid
import random
from werkzeug.security import generate_password_hash

DATABASE_NAME = 'satriajkn.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Tabel Pengguna
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT,
            password_hash TEXT,
            full_name TEXT,
            role TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # 2. Tabel Klaim (Data Transaksi Utama)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS klaim (
            klaim_id TEXT PRIMARY KEY,
            nomor_klaim TEXT UNIQUE,
            tgl_pengajuan TIMESTAMP,
            total_biaya REAL,
            status TEXT, -- Pending, Verified, Anomalous
            provider TEXT,
            diagnosis_code TEXT,
            tindakan_code TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # 3. Tabel Fraud Alert (Otak dari Sentinel - Hasil Analisis AI)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_alert (
            alert_id TEXT PRIMARY KEY,
            klaim_id TEXT,
            alert_level TEXT, -- High, Medium, Low
            reason_code TEXT, -- Upcoding, Phantom Billing, dll
            ai_confidence REAL, -- Skor keyakinan AI (0.0 - 1.0)
            description TEXT, -- Penjelasan agentic ("Biaya melebih ambang batas...")
            is_resolved INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            action TEXT,
            status TEXT,
            FOREIGN KEY (klaim_id) REFERENCES klaim(klaim_id)
        )
    ''')
    
    # 4. Tabel Audit Trail (Jejak Digital Nyata)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_trail (
            audit_id TEXT PRIMARY KEY,
            entity TEXT,
            entity_id TEXT,
            action TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            details TEXT
        )
    ''')

    # 5. Tabel Reports (Laporan)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            type TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            created_at TEXT,
            data TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Struktur Database Validasi (Arsitektur Sentinel).")

def seed_sample_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cek apakah data sudah ada agar tidak duplikat saat restart
    cursor.execute("SELECT COUNT(*) FROM klaim")
    if cursor.fetchone()[0] > 50:
        print("ℹ️  Data sudah ada. Melewati proses seeding.")
        conn.close()
        return
    
    print("🌱 Sedang menanam Data Pola Cerdas (Simulasi)...")

    # Buat User Admin
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?, ?)',
                  (str(uuid.uuid4()), 'admin', 'admin@bpjs.go.id', generate_password_hash('admin123'), 'Super Admin', 'admin'))

    # Skenario Data (Pattern Generation)
    providers = ['RSUD Cengkareng', 'RS Harapan Kita', 'Klinik Sehat Budi', 'Puskesmas Tebet', 'RS Hermina']
    diagnoses = ['J00', 'I10', 'E11', 'A09', 'Z00']
    
    today = datetime.now()
    
    # Loop membuat 400 data dummy
    for i in range(400): 
        klaim_id = str(uuid.uuid4())
        
        # Distribusi tanggal (acak dalam 1 tahun terakhir)
        days_back = int(random.triangular(0, 365, 30)) 
        tgl = (today - timedelta(days=days_back)).strftime('%Y-%m-%d %H:%M:%S')
        
        provider = random.choice(providers)
        biaya = random.randint(150000, 5000000)
        status = 'Verified'
        diagnosis = random.choice(diagnoses)
        
        # === INJEKSI LOGIKA FRAUD (Agar AI mendeteksi sesuatu) ===
        
        # Pola 1: Upcoding Masif di RSUD Cengkareng
        if provider == 'RSUD Cengkareng' and random.random() > 0.75:
            biaya = random.randint(15000000, 45000000) # Biaya sangat tinggi tidak wajar
            status = 'Anomalous'
            
            # Buat Alert
            alert_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO fraud_alert (alert_id, klaim_id, alert_level, reason_code, ai_confidence, description, created_at, status, action)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (alert_id, klaim_id, 'High', 'Upcoding', 0.98, 
                  f"Biaya Rp {biaya:,} terdeteksi 400% di atas rata-rata diagnosis {diagnosis}.", 
                  tgl, 'Open', 'Investigate'))
        
        # Pola 2: Phantom Billing (Klaim Fiktif) di Puskesmas Tebet
        elif provider == 'Puskesmas Tebet' and random.random() > 0.85:
            status = 'Anomalous'
            biaya = 250000 # Biaya kecil
            
            alert_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO fraud_alert (alert_id, klaim_id, alert_level, reason_code, ai_confidence, description, created_at, status, action)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (alert_id, klaim_id, 'Medium', 'Phantom Billing', 0.75, 
                  f"Terdeteksi pola klaim berulang identik dalam kurun waktu 24 jam.", 
                  tgl, 'Open', 'Review'))
            
        # Pola Normal (Sisanya random pending atau verified)
        else:
            if random.random() > 0.9: status = 'Pending'
        
        cursor.execute('''
            INSERT INTO klaim (klaim_id, nomor_klaim, tgl_pengajuan, total_biaya, status, provider, diagnosis_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (klaim_id, f"CLM-{2024}-{10000+i}", tgl, biaya, status, provider, diagnosis, tgl))

    conn.commit()
    conn.close()
    print("✅ Seeding Data Cerdas Selesai.")