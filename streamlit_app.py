"""
AI Destekli Müşteri Yorum Analiz Sistemi
Streamlit Frontend — FastAPI + DistilBERT
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─── Konfigürasyon ────────────────────────────────────────────────────────────
# Önce Streamlit Secrets (canlı ortam için), ardından .env veya varsayılan değerler
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "supersecret-demo-key-12345")

if "BACKEND_URL" in st.secrets:
    BACKEND_URL = st.secrets["BACKEND_URL"]
if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# ─── Sayfa Ayarları ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Duygu Analizi",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Arka plan */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* Hero kartı */
.hero-card {
    background: linear-gradient(135deg, rgba(102,126,234,0.25) 0%, rgba(118,75,162,0.25) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 24px;
    padding: 40px 50px;
    text-align: center;
    margin-bottom: 32px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}

.hero-subtitle {
    color: rgba(255,255,255,0.65);
    font-size: 1.1rem;
    font-weight: 400;
    margin-top: 10px;
}

/* Metrik kartları */
.metric-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #a78bfa;
}
.metric-label {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Sonuç banner */
.result-positive {
    background: linear-gradient(135deg, rgba(52,211,153,0.2), rgba(16,185,129,0.1));
    border: 1px solid rgba(52,211,153,0.4);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    animation: fadeSlideUp 0.5s ease-out;
}
.result-negative {
    background: linear-gradient(135deg, rgba(248,113,113,0.2), rgba(239,68,68,0.1));
    border: 1px solid rgba(248,113,113,0.4);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    animation: fadeSlideUp 0.5s ease-out;
}

.result-emoji   { font-size: 4rem; display: block; margin-bottom: 10px; }
.result-label   { font-size: 2.2rem; font-weight: 800; color: #ffffff; }
.result-score   { font-size: 1rem; color: rgba(255,255,255,0.7); margin-top: 6px; }

/* Güven çubuğu */
.confidence-bar-wrap {
    background: rgba(255,255,255,0.1);
    border-radius: 50px;
    height: 12px;
    width: 100%;
    margin-top: 16px;
    overflow: hidden;
}
.confidence-bar-fill-pos {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #34d399, #059669);
}
.confidence-bar-fill-neg {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #f87171, #dc2626);
}

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Textarea */
.stTextArea textarea {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(167,139,250,0.4) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.15rem !important;
    line-height: 1.6 !important;
    min-height: 350px !important;
}
.stTextArea textarea:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.2) !important;
}

/* Buton */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 40px !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 25px rgba(102,126,234,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 35px rgba(102,126,234,0.5) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.85) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

hr { border-color: rgba(255,255,255,0.1) !important; }

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(52,211,153,0.15);
    border: 1px solid rgba(52,211,153,0.3);
    border-radius: 50px;
    padding: 6px 16px;
    font-size: 0.85rem;
    color: #34d399;
    font-weight: 500;
}
.status-badge-offline {
    background: rgba(248,113,113,0.15);
    border-color: rgba(248,113,113,0.3);
    color: #f87171;
}

.history-item {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.9rem;
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)


# ─── Yardımcı Fonksiyonlar ─────────────────────────────────────────────────────
def check_backend_health() -> dict:
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return r.json()
    except Exception:
        return {"status": "offline", "model_loaded": False}


@st.cache_resource
def get_local_pipeline():
    from transformers import pipeline
    model_name = "savasy/bert-base-turkish-sentiment-cased"
    # Hugging Face pipeline'ı doğrudan streamlit içinde yükleniyor
    return pipeline(
        "sentiment-analysis",
        model=model_name,
        tokenizer=model_name,
        truncation=True,
        max_length=512,
    )


def analyze_text(text: str) -> dict | None:
    # Backend çevrimdışı ise modeli doğrudan yerel olarak Streamlit içinde çalıştır
    health = check_backend_health()
    if health.get("status") != "healthy":
        try:
            import time
            t0 = time.perf_counter()
            local_pipeline = get_local_pipeline()
            results = local_pipeline(text)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            
            result = results[0]
            label = result["label"].upper()
            score = result["score"]
            
            label_tr_map = {
                "POSITIVE": "POZİTİF 😊",
                "NEGATIVE": "NEGATİF 😞",
            }
            
            return {
                "sentiment": label,
                "sentiment_tr": label_tr_map.get(label, label),
                "score": round(score, 4),
                "confidence_pct": round(score * 100, 2),
                "processing_time_ms": round(elapsed_ms, 2),
                "text_length": len(text),
                "model": "savasy/bert-base-turkish-sentiment-cased (Standalone/Yerel Mod)",
            }
        except Exception as e:
            st.error(f"⚠️ Yerel model yükleme/analiz hatası: {str(e)}")
            return None

    # Backend çevrimiçi ise API isteği at
    try:
        r = requests.post(
            f"{BACKEND_URL}/analyze",
            json={"text": text},
            headers=HEADERS,
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"❌ API Hatası {r.status_code}: {r.json().get('detail', 'Bilinmeyen hata')}")
            return None
    except Exception as e:
        st.error(f"❗ Hata: {str(e)}")
        return None


# ─── Session State ─────────────────────────────────────────────────────────────
defaults = {
    "history": [],
    "total_analyses": 0,
    "positive_count": 0,
    "negative_count": 0,
    "pending_text": "",   # Örnek butonlardan gelen metin
    "last_result": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Örnek metin butonları — widget'lardan ÖNCE işlenmeli ─────────────────────
def set_positive_example():
    st.session_state.pending_text = (
        "Bu ürün inanılmaz derecede iyi! Kalitesi mükemmel ve kargo çok hızlıydı. "
        "Kesinlikle tavsiye ederim."
    )

def set_negative_example():
    st.session_state.pending_text = (
        "Çok kötü bir deneyimdi. Ürün bozuk geldi, müşteri hizmetleri hiç ilgilenmedi. "
        "Param boşa gitti."
    )


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Sistem Durumu")
    health = check_backend_health()
    if health.get("status") == "healthy":
        model_status = "✅ Model Hazır" if health.get("model_loaded") else "⏳ Model Yükleniyor..."
        st.markdown('<div class="status-badge">🟢 Backend Çevrimiçi</div>', unsafe_allow_html=True)
        st.markdown(f"<small style='color:#94a3b8'>{model_status}</small>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge" style="background: rgba(96, 165, 250, 0.15); border-color: rgba(96, 165, 250, 0.3); color: #60a5fa;">🔵 Yerel Model Aktif</div>', unsafe_allow_html=True)
        st.markdown("<small style='color:#94a3b8'>Stand-alone Mod (API Sunucusu Yok)</small>", unsafe_allow_html=True)

    st.divider()

    st.markdown("### 📊 İstatistikler")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam", st.session_state.total_analyses)
    c2.metric("😊 Poz.", st.session_state.positive_count)
    c3.metric("😞 Neg.", st.session_state.negative_count)

    st.divider()
    st.markdown("### ℹ️ Hakkında")
    st.markdown("""
    <small style='color:#94a3b8'>
    🤖 <b>Model:</b> DistilBERT<br>
    ⚡ <b>Backend:</b> FastAPI<br>
    🎨 <b>Frontend:</b> Streamlit<br>
    🔒 <b>Güvenlik:</b> API Key<br><br>
    Geliştirici: <b>Berat PALA</b>
    </small>
    """, unsafe_allow_html=True)


# ─── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-card">
    <h1 class="hero-title">🧠 AI Duygu Analizi</h1>
    <p class="hero-subtitle">
        DistilBERT destekli müşteri yorum analiz sistemi — anında, güvenilir, akıllı.
    </p>
</div>
""", unsafe_allow_html=True)


# ─── Ana İçerik ────────────────────────────────────────────────────────────────
col_main, col_right = st.columns([3, 2], gap="large")

with col_main:
    st.markdown("#### 📝 Analiz Edilecek Metin")

    # Hızlı örnek butonları (on_change callback ile güvenli)
    st.markdown("**💡 Hızlı örnekler:**")
    b1, b2 = st.columns(2)
    b1.button("😊 Pozitif Örnek", key="btn_pos", on_click=set_positive_example, use_container_width=True)
    b2.button("😞 Negatif Örnek", key="btn_neg", on_click=set_negative_example, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # pending_text varsa onu göster, sonra temizle
    initial_val = st.session_state.pending_text
    text_input = st.text_area(
        label="Yorum metni",
        value=initial_val,
        placeholder="Müşteri yorumunu buraya yazın veya yapıştırın...\n\nÖrnek: 'Bu ürün gerçekten harika, çok memnunum!'",
        height=350,
        label_visibility="hidden",
    )
    # Kullanıcı bir şey yazdıkça pending_text'i güncelle
    st.session_state.pending_text = text_input

    char_count = len(text_input)
    char_color = "#34d399" if char_count < 4000 else "#f87171"
    st.markdown(
        f"<small style='color:{char_color}'>{char_count} / 5000 karakter</small>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🔍 Analiz Et", key="analyze_btn", use_container_width=True)

with col_right:
    st.markdown("#### 🕒 Son Analizler")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            emoji = "😊" if item["sentiment"] == "POSITIVE" else "😞"
            color = "#34d399" if item["sentiment"] == "POSITIVE" else "#f87171"
            short = item['text'][:60] + ("..." if len(item['text']) > 60 else "")
            st.markdown(
                f"""<div class="history-item">
                    {emoji} <span style='color:{color};font-weight:600'>{item['sentiment_tr']}</span>
                    &nbsp;·&nbsp; <span style='opacity:0.6'>{item['confidence_pct']:.1f}%</span><br>
                    <small style='opacity:0.5'>{short}</small>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div class='history-item' style='opacity:0.5;text-align:center'>Henüz analiz yapılmadı.</div>",
            unsafe_allow_html=True,
        )


# ─── Analiz Sonucu ─────────────────────────────────────────────────────────────
if analyze_btn:
    if not text_input.strip():
        st.warning("⚠️ Lütfen analiz edilecek bir metin girin.")
    elif char_count > 5000:
        st.error("❌ Metin çok uzun! Maksimum 5000 karakter.")
    else:
        with st.spinner("🔄 DistilBERT analiz yapıyor..."):
            result = analyze_text(text_input)

        if result:
            st.session_state.total_analyses += 1
            if result["sentiment"] == "POSITIVE":
                st.session_state.positive_count += 1
            else:
                st.session_state.negative_count += 1

            st.session_state.history.append({
                "text": text_input,
                "sentiment": result["sentiment"],
                "sentiment_tr": result["sentiment_tr"],
                "confidence_pct": result["confidence_pct"],
            })
            st.session_state.last_result = result
            st.rerun()

# Sonuç göster (rerun sonrası)
if st.session_state.last_result and not analyze_btn:
    result = st.session_state.last_result
    st.markdown("---")
    st.markdown("### 🎯 Analiz Sonucu")

    is_positive = result["sentiment"] == "POSITIVE"
    css_class   = "result-positive" if is_positive else "result-negative"
    emoji       = "😊" if is_positive else "😞"
    bar_class   = "confidence-bar-fill-pos" if is_positive else "confidence-bar-fill-neg"
    conf        = result["confidence_pct"]

    st.markdown(f"""
    <div class="{css_class}">
        <span class="result-emoji">{emoji}</span>
        <div class="result-label">{result['sentiment_tr']}</div>
        <div class="result-score">Güven Skoru: <b>{conf:.2f}%</b></div>
        <div class="confidence-bar-wrap">
            <div class="{bar_class}" style="width:{conf}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in [
        (m1, f"{conf:.1f}%",                      "Güven"),
        (m2, f"{result['processing_time_ms']:.0f}","ms Süre"),
        (m3, str(result["text_length"]),            "Karakter"),
        (m4, "+" if is_positive else "−",           "Duygu"),
    ]:
        col.markdown(
            f'<div class="metric-card"><div class="metric-value">{val}</div>'
            f'<div class="metric-label">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 Ham API Yanıtı", expanded=False):
        st.json(result)


# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:rgba(255,255,255,0.3);font-size:0.8rem'>"
    "🧠 AI Duygu Analizi &nbsp;·&nbsp; DistilBERT + FastAPI + Streamlit"
    "&nbsp;·&nbsp; Geliştirici: <b>Berat PALA</b>"
    "</div>",
    unsafe_allow_html=True,
)
