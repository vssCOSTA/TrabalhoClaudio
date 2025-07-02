import os, joblib, numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import OrdCompra

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

class OCIn(BaseModel):
    nro: int
    fornecedor: int
    total: float = Field(..., gt=0)
    frete: float = Field(..., ge=0)
    qtde: float | None = None

class OCConfirmIn(OCIn):
    forma_pagamento: str

class OCRet(BaseModel):
    recomendado: str
    classes:     list[str]
    probs:       list[list[float]]

CLASSE_MAPEADA = {
    "Avista": "À vista",
    "10dias": "10 dias",
    "30dias": "30 dias",
    "2x": "Em 2x iguais",
    "3x": "Em 3x iguais",
}

@app.post("/oc", response_model=OCRet)
def criar_oc(req: OCIn):
    X = np.array([[req.total, req.frete]])
    prob_matrix = model.predict_proba(X)
    classes = model.classes_
    recomendado_bruto = classes[int(np.argmax(prob_matrix[0]))]
    recomendado = CLASSE_MAPEADA.get(recomendado_bruto, recomendado_bruto)

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

    return OCRet(
        recomendado=recomendado,
        classes=[CLASSE_MAPEADA.get(c, c) for c in classes],
        probs=prob_matrix.tolist()
    )

@app.post("/oc/predict", response_model=OCRet)
def prever_oc(req: OCIn):
    X = np.array([[req.total, req.frete]])
    prob_matrix = model.predict_proba(X)
    classes = model.classes_
    recomendado_bruto = classes[int(np.argmax(prob_matrix[0]))]
    recomendado = CLASSE_MAPEADA.get(recomendado_bruto, recomendado_bruto)
    return OCRet(
        recomendado=recomendado,
        classes=[CLASSE_MAPEADA.get(c, c) for c in classes],
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