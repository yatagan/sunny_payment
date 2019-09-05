from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    country = Column(String)
    city = Column(String)


class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True)
    currency = Column(String)
    balance = Column(Numeric, default=0)

    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="wallet")


Client.wallet = relationship("Wallet", uselist=False, back_populates="client")
