import sqlite3
import random
from datetime import datetime, timedelta

# Nama Database
DB_NAME = "satria_jkn.db"

# Koneksi ke Database
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 1. Inisialisasi Tabel (Schema)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🔨 Membuat tabel database...")

    # Tabel Peserta
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS peserta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        no_kartu TEXT UNIQUE NOT NULL,
        tanggal_lahir DATE,
        jenis_kelamin TEXT,
        alamat TEXT
    )
    ''')

    # Tabel Fasilitas Kesehatan (Faskes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faskes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        tipe TEXT, -- RS, Klinik, Puskesmas
        kota TEXT
    )
    ''')

    # Tabel Klaim
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS klaim (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nomor_klaim TEXT UNIQUE NOT NULL,
        peserta_id INTEGER,
        faskes_id INTEGER,
        tanggal DATE,
        diagnosis TEXT,
        tindakan TEXT,
        total_biaya INTEGER,
        status TEXT, -- Pending, Verified, Anomalous, Rejected
        FOREIGN KEY (peserta_id) REFERENCES peserta (id),
        FOREIGN KEY (faskes_id) REFERENCES faskes (id)
    )
    ''')

    # Tabel Fraud Alerts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fraud_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        klaim_id INTEGER,
        tipe_fraud TEXT, -- Upcoding, Fiktif, Duplikat, Unbundling
        risk_level TEXT, -- High, Medium, Low
        tanggal_deteksi DATE,
        status TEXT, -- Open, Resolved, Flagged
        deskripsi TEXT,
        FOREIGN KEY (klaim_id) REFERENCES klaim (id)
    )
    ''')

    # Tabel Audit Trail (Log)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_trail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        action TEXT,
        entity TEXT,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ Tabel berhasil dibuat.")

# 2. Generator Data Dummy
def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cek apakah data sudah ada
    cursor.execute('SELECT count(*) FROM peserta')
    if cursor.fetchone()[0] > 0:
        print("⚠️ Database sudah berisi data. Melewati proses seeding.")
        conn.close()
        return

    print("🌱 Mengisi data dummy...")

    # --- Data Master: Peserta ---
    names = ["Budi Santoso", "Siti Aminah", "Agus Pratama", "Dewi Lestari", "Eko Kurniawan", "Rina Mulyani", "Joko Susilo", "Sri Wahyuni", "Andi Wijaya", "Ratna Sari", "Hendra Gunawan", "Maya Putri"]
    alamat_list = ["Jl. Sudirman No. 1", "Jl. Merdeka No. 45", "Jl. Gatot Subroto", "Jl. Ahmad Yani", "Jl. Kebon Jeruk"]
    
    peserta_ids = []
    for i, nama in enumerate(names):
        no_kartu = f"000{random.randint(100000000, 999999999)}"
        tgl_lahir = (datetime.now() - timedelta(days=random.randint(7000, 20000))).strftime('%Y-%m-%d')
        gender = "L" if i % 2 == 0 else "P"
        cursor.execute('INSERT INTO peserta (nama, no_kartu, tanggal_lahir, jenis_kelamin, alamat) VALUES (?, ?, ?, ?, ?)', 
                       (nama, no_kartu, tgl_lahir, gender, random.choice(alamat_list)))
        peserta_ids.append(cursor.lastrowid)

    # --- Data Master: Faskes ---
    faskes_data = [
        ("RSUD Cengkareng", "RS", "Jakarta"),
        ("RS Harapan Kita", "RS", "Jakarta"),
        ("Klinik Sehat Budi", "Klinik", "Bandung"),
        ("Puskesmas Tebet", "Puskesmas", "Jakarta"),
        ("RS Santosa", "RS", "Bandung"),
        ("Klinik Permata", "Klinik", "Surabaya")
    ]
    
    faskes_ids = []
    for f in faskes_data:
        cursor.execute('INSERT INTO faskes (nama, tipe, kota) VALUES (?, ?, ?)', f)
        faskes_ids.append(cursor.lastrowid)

    # --- Data Transaksi: Klaim ---
    diagnoses = [
        ("J00", "Nasopharyngitis acute", 150000, 300000),
        ("A09", "Gastroenteritis", 500000, 1200000),
        ("I10", "Hypertension", 200000, 600000),
        ("E11", "Type 2 Diabetes", 400000, 1500000),
        ("K35", "Acute Appendicitis", 5000000, 12000000)
    ]

    statuses = ["Verified", "Verified", "Pending", "Pending", "Anomalous", "Rejected"]
    
    # Generate 100 klaim
    for i in range(100):
        p_id = random.choice(peserta_ids)
        f_id = random.choice(faskes_ids)
        diag_code, diag_name, min_cost, max_cost = random.choice(diagnoses)
        
        # Tanggal acak dalam 6 bulan terakhir
        tgl_klaim = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d')
        
        nomor_klaim = f"CLM-{datetime.now().year}-{10000+i}"
        biaya = random.randint(min_cost, max_cost)
        status = random.choice(statuses)

        # Skenario Fraud (Membuat data anomali)
        is_fraud = False
        if i % 15 == 0: # Setiap data ke-15 adalah fraud
            status = "Anomalous"
            biaya = biaya * 5 # Mark up biaya (Upcoding)
            is_fraud = True
        
        cursor.execute('''
            INSERT INTO klaim (nomor_klaim, peserta_id, faskes_id, tanggal, diagnosis, tindakan, total_biaya, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nomor_klaim, p_id, f_id, tgl_klaim, f"{diag_code} - {diag_name}", "Konsultasi & Obat", biaya, status))
        
        klaim_id = cursor.lastrowid

        # --- Data Transaksi: Alert Fraud ---
        if is_fraud:
            tipe_fraud = random.choice(["Upcoding", "Fiktif", "Unbundling"])
            risk = "High" if biaya > 5000000 else "Medium"
            cursor.execute('''
                INSERT INTO fraud_alerts (klaim_id, tipe_fraud, risk_level, tanggal_deteksi, status, deskripsi)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (klaim_id, tipe_fraud, risk, tgl_klaim, "Open", f"Biaya klaim {biaya} melebihi ambang batas wajar untuk diagnosis {diag_code}."))

    # --- Data Log Audit ---
    audit_logs = [
        ("Admin", "Login", "System", "User login success"),
        ("Verifikator", "Review", "Klaim", "Verified claim CLM-2025-10005"),
        ("System", "Detect", "Fraud Alert", "Detected anomaly in CLM-2025-10015"),
        ("Admin", "Update", "Settings", "Changed risk threshold")
    ]
    
    for log in audit_logs:
        cursor.execute('INSERT INTO audit_trail (user, action, entity, details) VALUES (?, ?, ?, ?)', log)

    conn.commit()
    conn.close()
    print("✅ Data dummy berhasil dibuat!")
    print(f"📍 Lokasi database: {DB_NAME}")

if __name__ == "__main__":
    init_db()
    seed_data()