"""
AI Destekli Müşteri Yorum Analiz Sistemi - Backend
FastAPI + DistilBERT ile duygu analizi
"""

import os
import time
import secrets
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# ─── Transformers (lazy import to speed startup) ───────────────────────────────
from transformers import pipeline

load_dotenv()

# ─── Configuration ─────────────────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY", "supersecret-demo-key-12345")
MODEL_NAME = "savasy/bert-base-turkish-sentiment-cased"

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# ─── Global model holder ────────────────────────────────────────────────────────
sentiment_pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the DistilBERT model on startup."""
    global sentiment_pipeline
    print(f"[INFO] Loading model: {MODEL_NAME} ...")
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        truncation=True,
        max_length=512,
    )
    print("[INFO] Model loaded successfully!")
    yield
    print("[INFO] Shutting down...")


# ─── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sentiment Analysis API",
    description="DistilBERT tabanlı müşteri yorum duygu analizi",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Security ───────────────────────────────────────────────────────────────────
async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Geçersiz API anahtarı. Lütfen X-API-Key header'ını kontrol edin.",
        )
    return api_key


# ─── Schemas ────────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Analiz edilecek metin")

    class Config:
        json_schema_extra = {
            "example": {"text": "Bu ürün gerçekten harika, çok memnunum!"}
        }


class AnalyzeResponse(BaseModel):
    sentiment: str
    sentiment_tr: str
    score: float
    confidence_pct: float
    processing_time_ms: float
    text_length: int
    model: str


LABEL_TR = {
    "POSITIVE": "POZİTİF 😊",
    "NEGATIVE": "NEGATİF 😞",
}

LABEL_EMOJI = {
    "POSITIVE": "✅",
    "NEGATIVE": "❌",
}


# ─── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": "Sentiment Analysis API çalışıyor 🚀",
        "model": MODEL_NAME,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    model_ready = sentiment_pipeline is not None
    return {
        "status": "healthy" if model_ready else "loading",
        "model_loaded": model_ready,
        "model": MODEL_NAME,
    }


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_sentiment(
    request: AnalyzeRequest,
    _: str = Depends(verify_api_key),
):
    """
    Verilen metnin duygu analizini yapar.

    - **text**: Analiz edilecek metin (max 5000 karakter)
    - **X-API-Key**: Header'da geçerli API anahtarı gerekli
    """
    if sentiment_pipeline is None:
        raise HTTPException(status_code=503, detail="Model henüz yüklenmedi, lütfen bekleyin.")

    t0 = time.perf_counter()
    try:
        results = sentiment_pipeline(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model hatası: {str(e)}")
    elapsed_ms = (time.perf_counter() - t0) * 1000

    result = results[0]
    label: str = result["label"].upper()  # POSITIVE / NEGATIVE
    score: float = result["score"]

    return AnalyzeResponse(
        sentiment=label,
        sentiment_tr=LABEL_TR.get(label, label),
        score=round(score, 4),
        confidence_pct=round(score * 100, 2),
        processing_time_ms=round(elapsed_ms, 2),
        text_length=len(request.text),
        model=MODEL_NAME,
    )


@app.post("/analyze/batch", tags=["Analysis"])
async def analyze_batch(
    texts: list[str],
    _: str = Depends(verify_api_key),
):
    """Birden fazla metni tek seferde analiz et (max 20)."""
    if len(texts) > 20:
        raise HTTPException(status_code=400, detail="Maksimum 20 metin gönderilebilir.")
    if sentiment_pipeline is None:
        raise HTTPException(status_code=503, detail="Model henüz yüklenmedi.")

    t0 = time.perf_counter()
    results = sentiment_pipeline(texts, truncation=True, max_length=512)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    output = []
    for text, r in zip(texts, results):
        label = r["label"].upper()
        output.append(
            {
                "text": text[:100] + ("..." if len(text) > 100 else ""),
                "sentiment": label,
                "sentiment_tr": LABEL_TR.get(label, label),
                "score": round(r["score"], 4),
                "confidence_pct": round(r["score"] * 100, 2),
            }
        )

    return {
        "results": output,
        "total": len(output),
        "processing_time_ms": round(elapsed_ms, 2),
    }
