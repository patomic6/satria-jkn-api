# SATRIA JKN - REST API

API untuk sistem deteksi fraud dan analisis klaim JKN (Jaminan Kesehatan Nasional).

## 🚀 Fitur

Berdasarkan mockup design, API ini menyediakan endpoint untuk:

1. **Dashboard** - Overview statistik dan metrics
2. **Claim Analysis** - Analisis klaim dengan deteksi anomali
3. **Alerts** - Manajemen fraud alerts (High/Medium/Low Risk)
4. **Audit Trail** - Log aktivitas sistem
5. **Reports** - Generate dan download laporan
6. **Settings** - Konfigurasi sistem

## 📋 Prerequisites

- Python 3.8+
- pip

## 🔧 Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Buat database
```bash
python database.py
```

3. Jalankan server:

```bash
python app.py
```

Server akan berjalan di `http://localhost:5000`

## 📚 API Endpoints

### Dashboard

- `GET /api/dashboard/overview` - Get overview statistics
- `GET /api/dashboard/trends` - Get claim trends chart data

### Peserta (Participants)

- `GET /api/peserta` - List all peserta
- `POST /api/peserta` - Create new peserta
- `GET /api/peserta/<id>` - Get peserta detail
- `PUT /api/peserta/<id>` - Update peserta
- `DELETE /api/peserta/<id>` - Delete peserta

### Fasilitas Kesehatan (Healthcare Facilities)

- `GET /api/faskes` - List all faskes
- `POST /api/faskes` - Create new faskes
- `GET /api/faskes/<id>` - Get faskes detail
- `PUT /api/faskes/<id>` - Update faskes
- `DELETE /api/faskes/<id>` - Delete faskes

### Klaim (Claims)

- `GET /api/klaim` - List all claims (supports filtering)
  - Query params: `?provider=<name>&status=<status>`
- `POST /api/klaim` - Create new claim
- `GET /api/klaim/<id>` - Get claim detail
- `PUT /api/klaim/<id>` - Update claim
- `DELETE /api/klaim/<id>` - Delete claim
- `GET /api/klaim/search?q=<query>` - Search claims
- `GET /api/klaim/anomaly-chart` - Get anomaly detection chart data

### Alerts

- `GET /api/alerts` - List all alerts
  - Query params: `?risk_level=<High|Medium|Low>`
- `POST /api/alerts` - Create new alert
- `GET /api/alerts/<id>` - Get alert detail
- `PUT /api/alerts/<id>` - Update alert
- `DELETE /api/alerts/<id>` - Delete alert
- `GET /api/alerts/summary` - Get alerts summary by risk level

### Audit Trail

- `GET /api/audit-trail` - List audit logs
  - Query params: `?entity=<entity>&action=<action>&user=<user>`
- `POST /api/audit-trail` - Create audit log
- `GET /api/audit-trail/<id>` - Get audit log detail

### Reports

- `GET /api/reports` - List generated reports
- `POST /api/reports/generate` - Generate new report
- `GET /api/reports/preview` - Get report preview data

### Diagnosis

- `GET /api/diagnosis` - List all diagnosis
- `POST /api/diagnosis` - Create new diagnosis
- `GET /api/diagnosis/<code>` - Get diagnosis detail
- `PUT /api/diagnosis/<code>` - Update diagnosis
- `DELETE /api/diagnosis/<code>` - Delete diagnosis

### Tindakan (Procedures)

- `GET /api/tindakan` - List all procedures
- `POST /api/tindakan` - Create new procedure
- `GET /api/tindakan/<code>` - Get procedure detail
- `PUT /api/tindakan/<code>` - Update procedure
- `DELETE /api/tindakan/<code>` - Delete procedure

### Settings

- `GET /api/settings` - Get system settings
- `PUT /api/settings` - Update system settings

### AI Recommendations

- `GET /api/ai/recommendations` - Get AI recommendations
  - Query params: `?klaim_id=<id>`
- `POST /api/ai/recommendations` - Create AI recommendation

### Pembayaran (Payments)

- `GET /api/pembayaran` - List payments
  - Query params: `?klaim_id=<id>`
- `POST /api/pembayaran` - Create new payment

## 📊 Data Models

API ini mengikuti schema dari `prisma.schema`:

- **Peserta** - Data peserta JKN
- **FasilitasKesehatan** - Data fasilitas kesehatan
- **Pelayanan** - Data pelayanan kesehatan
- **Diagnosis** - Master diagnosis (ICD codes)
- **Tindakan** - Master tindakan medis
- **RekamMedis** - Rekam medis pasien
- **Klaim** - Data klaim pembayaran
- **KlaimPelayanan** - Relasi klaim dengan pelayanan
- **Pembayaran** - Data pembayaran klaim
- **FraudAlert** - Alert deteksi fraud
- **ApiVerifikasiLog** - Log verifikasi API
- **AiRecommendation** - Rekomendasi dari AI
- **AuditTrail** - Log audit sistem

## 🎯 Sample Request

### Create New Claim

```bash
curl -X POST http://localhost:5000/api/klaim \
  -H "Content-Type: application/json" \
  -d '{
    "nomor_klaim": "CLM-12345",
    "total_biaya": 1000000,
    "status": "Pending",
    "provider": "Hospital A"
  }'
```

### Get Dashboard Overview

```bash
curl http://localhost:5000/api/dashboard/overview
```

### Search Claims

```bash
curl http://localhost:5000/api/klaim/search?q=CLM-12345
```

### Get Alerts by Risk Level

```bash
curl http://localhost:5000/api/alerts?risk_level=High
```

## 🔐 Security Notes

⚠️ **IMPORTANT**: Ini adalah mock implementation untuk development. Untuk production:

1. Implementasikan database yang sebenarnya (MySQL/PostgreSQL)
2. Tambahkan authentication & authorization
3. Implementasikan input validation
4. Tambahkan rate limiting
5. Gunakan HTTPS
6. Tambahkan logging yang proper
7. Implementasikan error handling yang lebih baik

## 📄 License

Copyright © 2025 SATRIA JKN
