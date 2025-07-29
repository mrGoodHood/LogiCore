from enum import StrEnum
from sqlalchemy.orm import mapped_column as mcol
from sqlalchemy.sql.functions import  func
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER, TEXT, VARCHAR, TIMESTAMP, BOOLEAN, ENUM, NUMERIC
from sqlalchemy import ForeignKey

from .user import BaseUser
from ..engine import Base


class ContractType(StrEnum):
    MASTER = 'MASTER'  # основной тип аккаунта создается по дефолту всем
    SHIPMENT = 'SHIPMENT'  # аккаунт для операций связанных с отправкой
    COD = 'COD'  # аккаунт для наложенных платежей
    RETURN = 'RETURN'  # аккаунт для возвратов


class Contract(Base):
    __tablename__ = "bill_contract"
    ID = mcol(BIGINT, primary_key=True, autoincrement=True, index=True)
    ParentID = mcol(BIGINT, index=True)
    Type = mcol(ENUM(ContractType, name='contract_type_enum'), default='MASTER', nullable=False)
    Number = mcol(VARCHAR(length=20), unique=True, nullable=False, index=True)
    Balance = mcol(NUMERIC(18, 4), nullable=False, default=0)
    IsActive = mcol(BOOLEAN, nullable=False, default=True)
    Note = mcol(TEXT)
    Created = mcol(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    Closed = mcol(TIMESTAMP(timezone=False))
    IsDeleted = mcol(BOOLEAN, nullable=False, default=False)


class ContractSettings(Base):
    __tablename__ = "bill_contract_settings"
    ID = mcol(BIGINT, primary_key=True, autoincrement=True, index=True)
    ContractID = mcol(ForeignKey(Contract.ID, ondelete="CASCADE"), nullable=False)
    Key = mcol(VARCHAR(length=100), nullable=False, index=True)
    Value = mcol(TEXT)
    Created = mcol(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    IsDeleted = mcol(BOOLEAN, nullable=False, default=False)


class Contract2User(Base):
    __tablename__ = "bill_contract2user"
    ID = mcol(INTEGER, primary_key=True, autoincrement=True, index=True)
    ContractID = mcol(ForeignKey(Contract.ID, ondelete="CASCADE"), nullable=False)
    UserID = mcol(ForeignKey(BaseUser.id, ondelete="RESTRICT"), nullable=False)
    BeginDateTime = mcol(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    EndDateTime = mcol(TIMESTAMP(timezone=False), nullable=True)
    IsDeleted = mcol(BOOLEAN, nullable=False, default=False)


class TransactionType(StrEnum):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'
    CORRECTION = 'CORRECTION'
