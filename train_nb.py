import os, joblib, pandas as pd
from sqlalchemy import create_engine
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.calibration import CalibratedClassifierCV
from dotenv import load_dotenv

# 1) Variáveis de ambiente
load_dotenv()
engine = create_engine(os.getenv("DB_URL"))

# 2) Ler histórico
df = pd.read_sql("""
    SELECT VlrTotal, VlrFrete, FPPagto
    FROM   OrdCompra
    WHERE  FPPagto IS NOT NULL
""", engine)

X = df[['VlrTotal', 'VlrFrete']]
y = df['FPPagto']

# 3) Modelo: scaler ➜ NB com smoothing ➜ calibração isotônica
gnb = Pipeline([
    ('sc', StandardScaler()),
    ('nb', GaussianNB(var_smoothing=1e-2))   # ajuste 1e-3 se quiser suavizar menos
])

model = CalibratedClassifierCV(gnb, method="isotonic", cv=5)

# 4) Treinar
model.fit(X, y)

# 5) Salvar
joblib.dump(model, os.getenv("MODEL_PATH"))
print("Modelo (suavizado + calibrado) salvo!")
