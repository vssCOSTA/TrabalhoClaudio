# main.py — versão que devolve matriz de probabilidades (valores 0-1)

import os, joblib, numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import OrdCompra

# ── configuração ──────────────────────────────────────────────────────
load_dotenv()
engine = create_engine(os.getenv("DB_URL"))
SessionLocal = sessionmaker(bind=engine)

model = joblib.load(os.getenv("MODEL_PATH"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── esquemas Pydantic ─────────────────────────────────────────────────
class OCIn(BaseModel):
    nro: int
    fornecedor: int
    total: float = Field(..., gt=0)
    frete: float = Field(..., ge=0)
    qtde: float | None = None

class OCConfirmIn(OCIn):
    forma_pagamento: str

class OCRet(BaseModel):
    recomendado: str           # classe de maior probabilidade
    classes:     list[str]     # cabeçalho da matriz
    probs:       list[list[float]]  # matriz (n_amostras × n_classes)

# ── endpoint ─────────────────────────────────────────────────────────
@app.post("/oc", response_model=OCRet)
def criar_oc(req: OCIn):
    # 1. Previsão
    X = np.array([[req.total, req.frete]])      # shape (1, 2)
    prob_matrix = model.predict_proba(X)        # shape (1, 4)
    classes = model.classes_
    recomendado = classes[int(np.argmax(prob_matrix[0]))]

    # 2. Persistir OC no banco (FPPagto ainda NULL)
    db = SessionLocal()
    db.add(OrdCompra(
        NroOrdemCompra=req.nro,
        CodFornecedor=req.fornecedor,
        QtdeTotal=req.qtde,
        VlrTotal=req.total,
        VlrFrete=req.frete
    ))
    db.commit()
    db.close()

    # 3. Retornar matriz de probabilidades brutas
    return OCRet(
        recomendado=recomendado,
        classes=list(classes),
        probs=prob_matrix.tolist()   # mantém formato [[..., ..., ... , ...]]
    )

@app.post("/oc/predict", response_model=OCRet)
def prever_oc(req: OCIn):
    X = np.array([[req.total, req.frete]])
    prob_matrix = model.predict_proba(X)
    classes = model.classes_
    recomendado = classes[int(np.argmax(prob_matrix[0]))]
    return OCRet(
        recomendado=recomendado,
        classes=list(classes),
        probs=prob_matrix.tolist()
    )

@app.post("/oc/confirm")
def confirmar_oc(req: OCConfirmIn):
    db = SessionLocal()
    db.add(OrdCompra(
        NroOrdemCompra=req.nro,
        CodFornecedor=req.fornecedor,
        QtdeTotal=req.qtde,
        VlrTotal=req.total,
        VlrFrete=req.frete,
        FPPagto=req.forma_pagamento
    ))
    db.commit()
    db.close()
    return {"status": "ok"}
