from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import json
import io
import random
from functools import wraps

# Import konfigurasi database dari file database.py
from database import get_db_connection, init_database, seed_sample_data

# Cek ketersediaan library untuk Report PDF (Opsional tapi disarankan)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORT_LIB_AVAILABLE = True
except ImportError:
    REPORT_LIB_AVAILABLE = False
    print("⚠️ ReportLab tidak ditemukan. Fitur download PDF mungkin terbatas.")

app = Flask(__name__)
# Izinkan CORS agar frontend (port 5173) bisa bicara dengan backend (port 5000)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ============================================
# 🧠 AI AGENTIC SIMULATION ENGINE
# ============================================
class FraudDetectionEngine:
    """
    Simulasi Logika 'Agentic AI' yang menganalisis klaim secara real-time
    berdasarkan pola historis dan aturan heuristik.
    """
    
    @staticmethod
    def analyze_claim(data):
        risk_score = 0.0
        reasons = []
        amount = float(data.get('total_biaya', 0))
        provider = data.get('provider', '')
        diagnosis = data.get('diagnosis_code', '')

        # --- 1. Analisis Biaya (Cost Anomaly) ---
        # Jika biaya > 20 juta, risiko naik drastis
        if amount > 20000000:
            risk_score += 0.6
            reasons.append(f"Biaya klaim Rp {amount:,} ekstrem melebihi ambang batas kewajaran regional.")
        elif amount > 10000000:
            risk_score += 0.3
            reasons.append("Biaya klaim berada di persentil ke-90 (High outlier).")
            
        # --- 2. Analisis Provider (Reputasi & Pola Historis) ---
        # Simulasi: Provider tertentu sedang dalam pengawasan Sentinel
        if 'Cengkareng' in provider: 
            risk_score += 0.25
            reasons.append(f"Provider {provider} sedang dalam status pengawasan audit aktif.")
        if 'Tebet' in provider and amount < 300000:
             risk_score += 0.4
             reasons.append(f"Pola frekuensi tinggi nilai rendah (indikasi Phantom Billing).")
            
        # --- 3. Analisis Integritas Data ---
        if not diagnosis:
            risk_score += 0.4
            reasons.append("Kode diagnosis hilang atau format tidak valid.")

        # Keputusan Agent
        is_fraud = risk_score > 0.5
        confidence = min(risk_score + 0.1, 0.99) # AI Confidence simulation
        
        explanation = " ".join(reasons) if reasons else "Data klaim konsisten dengan pola historis. Tidak ada anomali."
        
        # Tentukan tipe fraud untuk pelabelan
        fraud_type = "None"
        if is_fraud:
            if amount > 15000000: fraud_type = "Upcoding"
            elif "Tebet" in provider: fraud_type = "Phantom Billing"
            else: fraud_type = "Data Inconsistency"
        
        return {
            "is_fraud": is_fraud,
            "risk_level": "High" if risk_score > 0.7 else "Medium" if risk_score > 0.4 else "Low",
            "confidence": confidence,
            "fraud_type": fraud_type,
            "explanation": explanation
        }

# ============================================
# DATABASE & AUTH MIDDLEWARE
# ============================================

# Inisialisasi DB saat server start
init_database()
seed_sample_data()

def token_required(f):
    """Decorator sederhana untuk simulasi keamanan token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS': return f(*args, **kwargs)
        # Di development, kita izinkan token dummy 'dev-token-12345'
        token = request.headers.get('Authorization')
        if not token or 'dev-token' not in token:
            return jsonify({'message': 'Akses ditolak: Token tidak valid'}), 401
        return f(*args, **kwargs)
    return decorated

# ============================================
# DASHBOARD ENDPOINTS
# ============================================

@app.route('/api/dashboard/overview', methods=['GET'])
@token_required
def dashboard_overview():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hitung total klaim
    total = cursor.execute("SELECT COUNT(*) FROM klaim").fetchone()[0]
    
    # Hitung anomali aktif (yang belum di-resolve)
    active_anomalies = cursor.execute("SELECT COUNT(*) FROM fraud_alert WHERE status != 'Resolved'").fetchone()[0]
    
    # Hitung potensi uang negara yang diselamatkan (Total biaya dari klaim High Risk)
    savings = cursor.execute("""
        SELECT COALESCE(SUM(k.total_biaya), 0) 
        FROM klaim k 
        JOIN fraud_alert f ON k.klaim_id = f.klaim_id 
        WHERE f.alert_level = 'High' AND f.status != 'Resolved'
    """).fetchone()[0]
    
    pending = cursor.execute("SELECT COUNT(*) FROM klaim WHERE status = 'Pending'").fetchone()[0]
    conn.close()
    
    return jsonify({
        "total_claims": total,
        "detected_anomalies": active_anomalies,
        "potential_savings": savings,
        "pending_reviews": pending
    })

@app.route('/api/dashboard/trends', methods=['GET'])
@token_required
def dashboard_trends():
    """Data untuk grafik tren bulanan"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Mengambil data 6 bulan terakhir
    cursor.execute("""
        SELECT strftime('%Y-%m', tgl_pengajuan) as month,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'Anomalous' THEN 1 ELSE 0 END) as anomalies
        FROM klaim
        WHERE tgl_pengajuan > date('now', '-6 months')
        GROUP BY month
        ORDER BY month ASC
    """)
    
    result = []
    for row in cursor.fetchall():
        # Ubah format '2024-01' menjadi 'Jan'
        month_name = datetime.strptime(row['month'], '%Y-%m').strftime('%b')
        result.append({
            "name": month_name,
            "claims": row['total'],
            "anomalies": row['anomalies']
        })
    conn.close()
    return jsonify(result)

# ============================================
# KLAIM & SIMULASI AI (CORE LOGIC)
# ============================================

@app.route('/api/klaim', methods=['GET', 'POST'])
@token_required
def handle_klaim():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        # Ambil daftar klaim untuk tabel
        query = "SELECT nomor_klaim, provider, tgl_pengajuan as tanggal, total_biaya, status FROM klaim ORDER BY tgl_pengajuan DESC LIMIT 50"
        cursor.execute(query)
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(data)
        
    elif request.method == 'POST':
        # === SIMULASI REAL-TIME PROCESSING ===
        data = request.json
        
        # 1. Analisis Agentic dijalankan
        analysis = FraudDetectionEngine.analyze_claim(data)
        
        # 2. Simpan data dummy ke DB agar tercatat
        klaim_id = str(uuid.uuid4())
        tgl = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'Anomalous' if analysis['is_fraud'] else 'Pending'
        
        cursor.execute('''
            INSERT INTO klaim (klaim_id, nomor_klaim, tgl_pengajuan, total_biaya, status, provider, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (klaim_id, data.get('nomor_klaim'), tgl, data.get('total_biaya'), status, data.get('provider'), tgl))
        
        # 3. Jika Fraud, Buat Alert & Log Audit Otomatis
        if analysis['is_fraud']:
            alert_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO fraud_alert (alert_id, klaim_id, alert_level, reason_code, ai_confidence, description, created_at, status, action)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (alert_id, klaim_id, analysis['risk_level'], analysis['fraud_type'], 
                  analysis['confidence'], analysis['explanation'], tgl, 'Open', 'Auto-Flagged'))
            
            # Log Audit: AI mendeteksi sesuatu
            audit_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO audit_trail (audit_id, entity, entity_id, action, user, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (audit_id, 'AI Sentinel', klaim_id, 'DETECTED', 'System', f"AI detected {analysis['fraud_type']} risk", tgl))

        conn.commit()
        conn.close()
        
        # Return hasil analisis ke Frontend untuk ditampilkan di Sandbox
        return jsonify({
            'message': 'Klaim berhasil diproses oleh Sentinel',
            'analysis': analysis
        }), 201

@app.route('/api/klaim/anomaly-chart', methods=['GET'])
@token_required
def get_anomaly_chart():
    """Data untuk Pie Chart distribusi fraud"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT reason_code as name, COUNT(*) as value 
        FROM fraud_alert 
        GROUP BY reason_code
    """)
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"distribution": data})

# ============================================
# ALERTS & ACTIONS
# ============================================

@app.route('/api/alerts', methods=['GET'])
@token_required
def get_alerts():
    risk = request.args.get('risk_level')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT alert_id as id, reason_code as type, alert_level as risk_level, 
               created_at as date, status as alert_status
        FROM fraud_alert
    """
    params = []
    if risk:
        query += " WHERE alert_level = ?"
        params.append(risk)
        
    query += " ORDER BY created_at DESC LIMIT 20"
    cursor.execute(query, params)
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/alerts/<alert_id>', methods=['PUT'])
@token_required
def update_alert(alert_id):
    """Endpoint untuk user menyelesaikan (Resolve) alert"""
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    new_status = 'Resolved' if data.get('is_resolved') else 'Flagged'
    action_note = data.get('action', 'Updated manually')
    
    # Update status di DB
    cursor.execute("UPDATE fraud_alert SET status = ?, is_resolved = ? WHERE alert_id = ?", 
                  (new_status, 1 if new_status == 'Resolved' else 0, alert_id))
    
    # Catat di Audit Trail (Penting untuk transparansi)
    cursor.execute('''
        INSERT INTO audit_trail (audit_id, entity, entity_id, action, user, details)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), 'Alert', alert_id, new_status.upper(), 'Admin User', action_note))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Alert updated'}), 200

# ============================================
# AUDIT TRAIL & REPORTS
# ============================================

@app.route('/api/audit-trail', methods=['GET'])
@token_required
def get_audit_trail():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_trail ORDER BY timestamp DESC LIMIT 30")
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/reports', methods=['GET'])
@token_required
def get_reports_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT report_id as id, type as name, created_at as date, status FROM reports ORDER BY created_at DESC")
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/reports/generate', methods=['POST'])
@token_required
def generate_report():
    """Simulasi pembuatan laporan baru"""
    rpt_type = request.json.get('type', 'Fraud Summary')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ambil data ringkasan nyata dari DB
    cursor.execute("SELECT COUNT(*) FROM klaim")
    total_c = cursor.fetchone()[0]
    cursor.execute("SELECT alert_level, COUNT(*) FROM fraud_alert GROUP BY alert_level")
    alerts_data = {r[0]: r[1] for r in cursor.fetchall()}
    
    report_payload = {
        "total_claims": total_c,
        "fraud_by_level": alerts_data,
        "generated_by": "SATRIA JKN Agent"
    }
    
    rep_id = f"RP-{uuid.uuid4().hex[:6].upper()}"
    tgl = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute("INSERT INTO reports (report_id, type, created_at, status, data) VALUES (?, ?, ?, ?, ?)",
                  (rep_id, rpt_type, tgl, 'Ready', json.dumps(report_payload)))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Report generated', 'report_id': rep_id})

@app.route('/api/reports/<report_id>/download', methods=['GET'])
def download_report(report_id):
    """Generate PDF fisik secara on-the-fly"""
    if not REPORT_LIB_AVAILABLE:
        return jsonify({'error': 'Library PDF (reportlab) belum diinstall di server.'}), 500

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,))
    report = cursor.fetchone()
    conn.close()
    
    if not report: return jsonify({'error': 'Report not found'}), 404
    
    # Buat PDF di memori (tanpa simpan file fisik)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Header Laporan
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "SATRIA JKN - SENTINEL REPORT")
    c.line(100, 740, 500, 740)
    
    # Detail Laporan
    c.setFont("Helvetica", 12)
    c.drawString(100, 710, f"Report ID : {report_id}")
    c.drawString(100, 690, f"Type      : {report['type']}")
    c.drawString(100, 670, f"Date      : {report['created_at']}")
    
    # Isi Data
    c.drawString(100, 630, "Summary Statistics:")
    data = json.loads(report['data'])
    y = 610
    for k, v in data.items():
        # Format text agar rapi
        text = f"- {k.replace('_', ' ').title()}: {v}"
        c.drawString(120, y, text)
        y -= 20
        
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 100, "Generated by SATRIA JKN Agentic AI System.")
    
    c.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"SATRIA-{report_id}.pdf", mimetype='application/pdf')

@app.route('/api/settings', methods=['GET'])
@token_required
def get_settings():
    return jsonify({
        "system_name": "SATRIA JKN Sentinel",
        "version": "2.5.0-Stable",
        "mode": "Agentic Simulation"
    })

if __name__ == "__main__":
    print("🚀 SATRIA JKN Sentinel Engine Starting...")
    print("🧠 AI Agentic Logic: ACTIVE")
    print("📡 Server running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)