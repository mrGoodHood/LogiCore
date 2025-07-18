from enum import Enum
from sqlalchemy.orm import mapped_column as mcol
from sqlalchemy.sql.functions import func
from sqlalchemy.dialects.postgresql import (
    SMALLINT, ARRAY, UUID, BIGINT, INTEGER, TEXT, BYTEA,
    JSONB, VARCHAR, TIMESTAMP, BOOLEAN, DATE, MONEY, ENUM as PgEnum, NUMERIC
)
from sqlalchemy import ForeignKey, DDL, event
from .billing import Contract
from .user import BaseUser
from ..engine import Base


class BatchStatusEnum(Enum):
    CREATED = 'CREATED'
    FROZEN = 'FROZEN'
    ACCEPTED = 'ACCEPTED'
    SENT = 'SENT'
    ARCHIVED = 'ARCHIVED'


class Batch(Base):
    __tablename__ = "ship_batch"
    ID = mcol(BIGINT, primary_key=True, autoincrement=True, index=True)
    ContractID = mcol(ForeignKey(Contract.ID, ondelete="CASCADE"), nullable=False)
    UserID = mcol(ForeignKey(BaseUser.id, ondelete="CASCADE"), nullable=False)
    BatchName = mcol(VARCHAR(length=100), unique=True, nullable=False, index=True)
    BatchCategory = mcol(VARCHAR(length=100))
    BatchStatus = mcol(PgEnum(BatchStatusEnum, name='batch_status_enum'), nullable=False)
    BatchStatusDate = mcol(TIMESTAMP(timezone=False))
    BatchSentDate = mcol(DATE, nullable=False)
    PostOfficeCode = mcol(VARCHAR(length=20), nullable=False)
    PostOfficeName = mcol(VARCHAR(length=256), nullable=False)
    PostOfficeAddress = mcol(VARCHAR(length=256))
    Mass = mcol(INTEGER, nullable=False)
    ShipmentCount = mcol(INTEGER, nullable=False)
    TotalRate = mcol(INTEGER, nullable=False)
    TotalRateVat = mcol(INTEGER, nullable=False)
    Created = mcol(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    IsDeleted = mcol(BOOLEAN, nullable=False, default=False)


class BatchDoc(Base):
    __tablename__ = "ship_batch_doc"
    BatchID = mcol(ForeignKey(Batch.ID, ondelete="CASCADE"), nullable=False,  primary_key=True)
    Document = mcol(BYTEA, nullable=False)
    Created = mcol(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    IsDeleted = mcol(BOOLEAN, nullable=False, default=False)
