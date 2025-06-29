from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, CHAR

Base = declarative_base()

class OrdCompra(Base):
    __tablename__ = "OrdCompra"
    NroOrdemCompra = Column(Integer, primary_key=True)
    CodFornecedor  = Column(Integer, nullable=False)
    QtdeTotal      = Column(Float)
    VlrTotal       = Column(Float)
    VlrFrete       = Column(Float)
    FPPagto        = Column(CHAR(10))
