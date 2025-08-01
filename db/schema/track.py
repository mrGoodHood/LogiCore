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


class TrackBarcodeTicket(Base):
    __tablename__ = "track_ticket_barcode"
    ID = mcol(BIGINT, primary_key=True, autoincrement=True, index=True)
    BarcodeID = mcol(ForeignKey(Barcode.ID, ondelete="CASCADE"), nullable=False)
    TicketID = mcol(ForeignKey(TrackTicket.ID, ondelete="CASCADE"), nullable=False)


class TrackMailCategory(Base):
    __tablename__ = "track_mail_category"
    ID = mcol(SMALLINT, primary_key=True, autoincrement=True, index=True)
    Value = mcol(VARCHAR(length=256), nullable=False)
    Description = mcol(VARCHAR(length=256), nullable=False)
    VerboseName = mcol(VARCHAR(length=256))
    IsCODExists = mcol(BOOLEAN, nullable=False)
