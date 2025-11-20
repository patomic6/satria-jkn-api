# API Documentation - SATRIA JKN

## 📖 Daftar Lengkap Endpoint API

### Base URL

```
http://localhost:5000
```

---

## 🏠 Dashboard Endpoints

### 1. Get Dashboard Overview

Mendapatkan ringkasan statistik dashboard

**Endpoint:** `GET /api/dashboard/overview`

**Response:**

```json
{
  "total_claims": "300M",
  "detected_anomalies": "5-10%",
  "fraud_alerts": {
    "active": 120,
    "total": 150
  },
  "savings": "Rp5-10T",
  "recent_alerts": [...]
}
```

### 2. Get Claim Trends

Mendapatkan data tren klaim untuk chart

**Endpoint:** `GET /api/dashboard/trends`

**Response:**

```json
{
  "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  "claims": [25, 28, 26, 30, 29, 30],
  "anomalies": [2, 3, 2, 3, 2, 3]
}
```

---

## 💰 Klaim (Claims) Endpoints

### 1. Get All Claims

Mendapatkan semua data klaim

**Endpoint:** `GET /api/klaim`

**Query Parameters:**

- `provider` (optional) - Filter berdasarkan provider
- `status` (optional) - Filter berdasarkan status

**Example:**

```
GET /api/klaim?status=Anomalous&provider=Hospital%20A
```

### 2. Create Claim

Membuat klaim baru

**Endpoint:** `POST /api/klaim`

**Request Body:**

```json
{
  "nomor_klaim": "CLM-12345",
  "tgl_pengajuan": "2025-11-10",
  "total_biaya": 1000000,
  "status": "Pending",
  "provider": "Hospital A"
}
```

**Response:**

```json
{
  "klaim_id": "uuid-here",
  "nomor_klaim": "CLM-12345",
  "tgl_pengajuan": "2025-11-10",
  "total_biaya": 1000000,
  "status": "Pending",
  "provider": "Hospital A",
  "created_at": "2025-11-13T..."
}
```

### 3. Get Claim Detail

Mendapatkan detail klaim spesifik

**Endpoint:** `GET /api/klaim/<klaim_id>`

### 4. Update Claim

Update data klaim

**Endpoint:** `PUT /api/klaim/<klaim_id>`

**Request Body:**

```json
{
  "status": "Approved",
  "total_biaya": 1200000
}
```

### 5. Delete Claim

Menghapus klaim

**Endpoint:** `DELETE /api/klaim/<klaim_id>`

### 6. Search Claims

Mencari klaim berdasarkan keyword

**Endpoint:** `GET /api/klaim/search?q=<query>`

**Example:**

```
GET /api/klaim/search?q=CLM-001
```

### 7. Get Anomaly Chart Data

Mendapatkan data chart deteksi anomali

**Endpoint:** `GET /api/klaim/anomaly-chart`

**Response:**

```json
{
  "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
  "normal": [45, 50, 48, 52],
  "anomalous": [5, 8, 6, 7]
}
```

---

## 🚨 Alerts Endpoints

### 1. Get All Alerts

Mendapatkan semua alerts

**Endpoint:** `GET /api/alerts`

**Query Parameters:**

- `risk_level` (optional) - Filter berdasarkan risk level (High/Medium/Low)

**Example:**

```
GET /api/alerts?risk_level=High
```

### 2. Create Alert

Membuat alert baru

**Endpoint:** `POST /api/alerts`

**Request Body:**

```json
{
  "klaim_id": "CL001",
  "alert_level": "High",
  "reason_code": "Upcoding",
  "action": "Investigate"
}
```

### 3. Get Alert Detail

Mendapatkan detail alert

**Endpoint:** `GET /api/alerts/<alert_id>`

### 4. Update Alert

Update alert

**Endpoint:** `PUT /api/alerts/<alert_id>`

**Request Body:**

```json
{
  "is_resolved": true,
  "resolved_at": "2025-11-13T..."
}
```

### 5. Delete Alert

Menghapus alert

**Endpoint:** `DELETE /api/alerts/<alert_id>`

### 6. Get Alerts Summary

Mendapatkan ringkasan alerts berdasarkan risk level

**Endpoint:** `GET /api/alerts/summary`

**Response:**

```json
{
  "high_risk": 50,
  "medium_risk": 40,
  "low_risk": 30
}
```

---

## 📝 Audit Trail Endpoints

### 1. Get All Audit Logs

Mendapatkan semua log audit

**Endpoint:** `GET /api/audit-trail`

**Query Parameters:**

- `entity` (optional) - Filter berdasarkan entity
- `action` (optional) - Filter berdasarkan action
- `user` (optional) - Filter berdasarkan user

**Example:**

```
GET /api/audit-trail?entity=Klaim&user=Admin
```

### 2. Create Audit Log

Membuat log audit baru

**Endpoint:** `POST /api/audit-trail`

**Request Body:**

```json
{
  "entity": "Klaim",
  "entity_id": "CL001",
  "action": "Verified Claim",
  "user": "Admin",
  "details": "Claim ID: CL001"
}
```

### 3. Get Audit Log Detail

Mendapatkan detail audit log

**Endpoint:** `GET /api/audit-trail/<audit_id>`

---

## 📊 Reports Endpoints

### 1. Get All Reports

Mendapatkan list laporan yang sudah dibuat

**Endpoint:** `GET /api/reports`

**Response:**

```json
[
  {
    "report_id": "RP001",
    "type": "Fraud Summary",
    "date": "2025-11-10",
    "status": "Ready",
    "download_url": "/api/reports/RP001/download"
  }
]
```

### 2. Generate Report

Generate laporan baru

**Endpoint:** `POST /api/reports/generate`

**Request Body:**

```json
{
  "type": "Fraud Summary",
  "date_range": "2025-11-01 to 2025-11-30"
}
```

### 3. Get Report Preview

Mendapatkan preview data laporan

**Endpoint:** `GET /api/reports/preview`

**Response:**

```json
{
  "chart_type": "bar",
  "labels": ["High Risk", "Medium Risk", "Low Risk"],
  "values": [50, 40, 30]
}
```

---

## 👥 Peserta Endpoints

### 1. Get All Peserta

**Endpoint:** `GET /api/peserta`

### 2. Create Peserta

**Endpoint:** `POST /api/peserta`

**Request Body:**

```json
{
  "status_keanggotaan": "Active",
  "segmentasi": "Regular"
}
```

### 3. Get/Update/Delete Peserta

- `GET /api/peserta/<peserta_id>`
- `PUT /api/peserta/<peserta_id>`
- `DELETE /api/peserta/<peserta_id>`

---

## 🏥 Fasilitas Kesehatan Endpoints

### 1. Get All Faskes

**Endpoint:** `GET /api/faskes`

### 2. Create Faskes

**Endpoint:** `POST /api/faskes`

**Request Body:**

```json
{
  "kode_faskes": "HOSP-C",
  "tipe": "Hospital",
  "wilayah": "Surabaya",
  "status": "Active"
}
```

### 3. Get/Update/Delete Faskes

- `GET /api/faskes/<faskes_id>`
- `PUT /api/faskes/<faskes_id>`
- `DELETE /api/faskes/<faskes_id>`

---

## 🩺 Diagnosis Endpoints

### 1. Get All Diagnosis

**Endpoint:** `GET /api/diagnosis`

### 2. Create Diagnosis

**Endpoint:** `POST /api/diagnosis`

**Request Body:**

```json
{
  "code": "A03",
  "nama": "Shigellosis",
  "deskripsi": "Bacterial infection"
}
```

### 3. Get/Update/Delete Diagnosis

- `GET /api/diagnosis/<code>`
- `PUT /api/diagnosis/<code>`
- `DELETE /api/diagnosis/<code>`

---

## 💉 Tindakan Endpoints

### 1. Get All Tindakan

**Endpoint:** `GET /api/tindakan`

### 2. Create Tindakan

**Endpoint:** `POST /api/tindakan`

**Request Body:**

```json
{
  "code": "T003",
  "nama": "Operasi",
  "tarif_standar": 5000000
}
```

### 3. Get/Update/Delete Tindakan

- `GET /api/tindakan/<code>`
- `PUT /api/tindakan/<code>`
- `DELETE /api/tindakan/<code>`

---

## ⚙️ Settings Endpoints

### 1. Get Settings

**Endpoint:** `GET /api/settings`

**Response:**

```json
{
  "notification": {
    "email": true,
    "in_app": true
  },
  "theme": "Light",
  "api_integrations": ["BPJS", "Internal"],
  "alert_thresholds": {
    "high": 80,
    "medium": 50,
    "low": 20
  }
}
```

### 2. Update Settings

**Endpoint:** `PUT /api/settings`

**Request Body:**

```json
{
  "notification": {
    "email": false,
    "in_app": true
  },
  "theme": "Dark"
}
```

---

## 🤖 AI Recommendations Endpoints

### 1. Get AI Recommendations

**Endpoint:** `GET /api/ai/recommendations`

**Query Parameters:**

- `klaim_id` (optional) - Filter berdasarkan klaim

### 2. Create AI Recommendation

**Endpoint:** `POST /api/ai/recommendations`

**Request Body:**

```json
{
  "klaim_id": "CL001",
  "agent_version": "v1.0",
  "score": 0.85,
  "rekomendasi": "Investigate further"
}
```

---

## 💳 Pembayaran Endpoints

### 1. Get Payments

**Endpoint:** `GET /api/pembayaran`

**Query Parameters:**

- `klaim_id` (optional) - Filter berdasarkan klaim

### 2. Create Payment

**Endpoint:** `POST /api/pembayaran`

**Request Body:**

```json
{
  "klaim_id": "CL001",
  "jumlah": 1000000,
  "status_pembayaran": "Completed",
  "metode_pembayaran": "Transfer"
}
```

---

## 🔒 Error Responses

Semua endpoint dapat mengembalikan error responses berikut:

### 404 Not Found

```json
{
  "error": "Resource not found"
}
```

### 400 Bad Request

```json
{
  "error": "Invalid request data"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

---

## 🧪 Testing dengan cURL

### Example 1: Get Dashboard Overview

```bash
curl http://localhost:5000/api/dashboard/overview
```

### Example 2: Create New Claim

```bash
curl -X POST http://localhost:5000/api/klaim \
  -H "Content-Type: application/json" \
  -d '{
    "nomor_klaim": "CLM-12345",
    "total_biaya": 1000000,
    "status": "Pending"
  }'
```

### Example 3: Get High Risk Alerts

```bash
curl "http://localhost:5000/api/alerts?risk_level=High"
```

### Example 4: Search Claims

```bash
curl "http://localhost:5000/api/klaim/search?q=CL001"
```

---

## 📱 Mapping dengan Mockup

| Mockup Page             | API Endpoints                                      |
| ----------------------- | -------------------------------------------------- |
| Dashboard (page 1)      | `/api/dashboard/overview`, `/api/dashboard/trends` |
| Claim Analysis (page 2) | `/api/klaim`, `/api/klaim/anomaly-chart`           |
| Alerts (page 3)         | `/api/alerts`, `/api/alerts/summary`               |
| Audit Trail (page 4)    | `/api/audit-trail`                                 |
| Reports (page 5)        | `/api/reports`, `/api/reports/generate`            |
| Settings (page 6)       | `/api/settings`                                    |

---

## 🚀 Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run server:

```bash
python app.py
```

3. Test API:

```bash
python test_api.py
```

4. Import Postman collection:

- Open Postman
- Import `postman_collection.json`
- Start testing!
