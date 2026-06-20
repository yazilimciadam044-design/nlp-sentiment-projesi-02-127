# AI Destekli Müşteri Yorum Analiz Sistemi

> DistilBERT + FastAPI + Streamlit ile güçlendirilmiş gerçek zamanlı duygu analizi platformu.

---

## 🚀 Hızlı Başlangıç

### 1. Bağımlılıkları Kur

```bash
# Backend bağımlılıkları
pip install -r backend/requirements.txt

# Frontend bağımlılıkları
pip install -r frontend/requirements.txt
```

### 2. Backend'i Başlat (Terminal 1)

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

İlk çalıştırmada DistilBERT modeli (~260MB) otomatik indirilir.  
API dokümantasyonu: http://localhost:8000/docs

### 3. Frontend'i Başlat (Terminal 2)

```bash
streamlit run streamlit_app.py
```

Tarayıcıda http://localhost:8501 adresine gidin.

---

## 🏗️ Mimari

```
nlp-sentiment-projesi02/
├── backend/
│   ├── app.py              # FastAPI + DistilBERT
│   └── requirements.txt
├── frontend/
│   ├── app.py              # (yedek)
│   └── requirements.txt
├── streamlit_app.py        # Ana Streamlit UI
├── .env                    # API Key ve URL ayarları
├── .gitignore
└── README.md
```

## 🔒 Güvenlik

API Key `.env` dosyasında tanımlıdır. Tüm istekler `X-API-Key` header'ı gerektirir.

```
API_KEY=supersecret-demo-key-12345
```

## 📡 API Endpoint'leri

| Method | Endpoint        | Açıklama                |
|--------|-----------------|-------------------------|
| GET    | `/`             | Servis durumu           |
| GET    | `/health`       | Model hazırlık durumu   |
| POST   | `/analyze`      | Tek metin analizi       |
| POST   | `/analyze/batch`| Toplu metin analizi     |

## 🛠️ Teknolojiler

| Katman    | Teknoloji                              |
|-----------|----------------------------------------|
| Model     | DistilBERT (SST-2, HuggingFace)        |
| Backend   | FastAPI + Uvicorn                      |
| Frontend  | Streamlit                              |
| Güvenlik  | API Key (Header tabanlı)               |

---

Geliştirici: **Berat PALA**
