import datetime
import enum

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Date, DateTime, Enum
from sqlalchemy.orm import relationship


Base = declarative_base()


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
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


class CurrencyRate(Base):
    __tablename__ = 'currency_rate'

    date = Column(Date, primary_key=True)
    currency = Column(String, primary_key=True)
    rate = Column(Numeric)


class TransactionTypeEnum(enum.Enum):
    refill = 1
    transfer = 2


class TransactionLog(Base):
    __tablename__ = 'transaction_logs'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)
    type = Column(Enum(TransactionTypeEnum))

    wallet_id_from = Column(Integer, ForeignKey('wallets.id'))
    wallet_id_to = Column(Integer, ForeignKey('wallets.id'))

    wallet_from = relationship('Wallet', foreign_keys=[wallet_id_from])
    wallet_to = relationship('Wallet', foreign_keys=[wallet_id_to])

    amount = Column(Numeric)
    exchange_rate = Column(Numeric)
