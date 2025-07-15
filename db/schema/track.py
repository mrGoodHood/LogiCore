from sqlalchemy.orm import mapped_column as mcol
from sqlalchemy.sql.functions import func
from sqlalchemy.dialects.postgresql import (
    SMALLINT, ARRAY, UUID, BIGINT, INTEGER, TEXT,
    JSONB, VARCHAR, TIMESTAMP, BOOLEAN, DATE, MONEY, ENUM, NUMERIC
)
from sqlalchemy import ForeignKey, DDL, event
from .shipment import Barcode
from ..engine import Base


class TrackTicket(Base):
    __tablename__ = "track_ticket"
    ID = mcol(BIGINT, primary_key=True, autoincrement=True, index=True)
    Value = mcol(VARCHAR(length=256), nullable=False)
    CheckDate = mcol(TIMESTAMP(timezone=False), server_default=func.current_timestamp(), nullable=False)
    Created = mcol(TIMESTAMP(timezone=False), server_default=func.current_timestamp(), nullable=False)