import os, joblib, pandas as pd
from sqlalchemy import create_engine
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.calibration import CalibratedClassifierCV
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DB_URL"))

df = pd.read_sql("""
    SELECT VlrTotal, VlrFrete, FPPagto
    FROM   OrdCompra
    WHERE  FPPagto IS NOT NULL
""", engine)

X = df[['VlrTotal', 'VlrFrete']]
y = df['FPPagto']

gnb = Pipeline([
    ('sc', StandardScaler()),
    ('nb', GaussianNB(var_smoothing=1e-2))
])

model = CalibratedClassifierCV(gnb, method="isotonic", cv=5)
model.fit(X, y)
joblib.dump(model, os.getenv("MODEL_PATH"))
print("Modelo (suavizado + calibrado) salvo!")