class TrackSummaryFilter(StrEnum):
    IS_RETURNED = "is_returned"
    IS_HOT = "is_hot"
    IS_NOT_HOT = "is_not_hot"
    IS_HANGING = "is_hanging"


class TrackSummarySort(StrEnum):
    TRACK_STATUS = "track_status"
    BATCH_SENT_DATE = "batch_sent_date"


def set_track_summary_filter(query: Select, query_filter: Optional[TrackSummaryFilter]) -> Select:
    if query_filter == TrackSummaryFilter.IS_RETURNED:
        return query.where(TrackSummary.IsReturned == True)
    elif query_filter == TrackSummaryFilter.IS_HOT:
        return query.where(TrackSummary.IsHot == True)
    elif query_filter == TrackSummaryFilter.IS_NOT_HOT:
        return query.where(TrackSummary.IsHot == False)
    elif query_filter == TrackSummaryFilter.IS_HANGING:
        month_ago = datetime.today() - relativedelta(months=+1)
        return query.where(
            and_(
                TrackSummary.IsHot == True,
                TrackShipHistory.OperationDate < month_ago,
            )
        )
    return query


def set_track_summary_sort(query: Select, sort: Optional[TrackSummarySort], sort_desc: bool) -> Select:
    if sort == TrackSummarySort.TRACK_STATUS:
        if sort_desc:
            query = query.order_by(TrackShipStatus.OperationName.desc())
        else:
            query = query.order_by(TrackShipStatus.OperationName.asc())
    elif sort == TrackSummarySort.BATCH_SENT_DATE:
        if sort_desc:
            query = query.order_by(Batch.BatchSentDate.desc())
        else:
            query = query.order_by(Batch.BatchSentDate.asc())

    return query.order_by(Barcode.ID)

def set_batch_name_filter(query: Select, batch_name: str) -> Select:
    return query.where(Batch.BatchName == batch_name)

def set_track_summary_search_query(query: Select, search_query: str) -> Select:
    return query.filter
        or_(
            Barcode.OrderNum.like("%" + search_query + "%"),
            Barcode.Barcode.like("%" + search_query + "%"),
            Barcode.IndexFrom.like("%" + search_query + "%"),
            Barcode.IndexTo.like("%" + search_query + "%"),
        )
    )


async def get_track_summary_info(
    user_id: UUID,
    page: int,
    page_size: int,
    sort_desc: bool,
    batch_name: Optional[str],
    search_query: Optional[str],
    sort: Optional[TrackSummarySort],
    query_filter: Optional[TrackSummaryFilter],
) -> list[dict[str, Any]]:
    async with async_session_maker() as session:
        ShipPointFrom = aliased(ShipPoint)
        ShipPointTo = aliased(ShipPoint)

        statement = (
            select(
                Contract2User.ID,
                Barcode.OrderNum,
                Barcode.Barcode,
                Barcode.IndexFrom,
                Barcode.IndexTo,
                TrackShipStatus.OperationName,
                TrackShipHistory.OperationDate,
                Barcode.MailType,
                TrackCODStatus.OperationName,
                TrackCODHistory.OperationDate,
                Barcode.Mass,
                Batch.BatchName,
                Batch.BatchSentDate,
                Batch.PostOfficeCode,
                Barcode.TotalRate,
                Barcode.TotalRateVat,
                Barcode.CODPayment,
                ShipPointFrom.Region,
                ShipPointFrom.District,
                ShipPointFrom.Settlement,
                ShipPointFrom.AddressSource,
                ShipPointTo.Region,
                ShipPointTo.District,
                ShipPointTo.Settlement,
                ShipPointTo.AddressSource,
            )
            .join(Contract, Contract2User.ContractID == Contract.ID)
            .join(Batch, Contract.ID == Batch.ContractID)
            .join(Barcode, Batch.ID == Barcode.BatchID)
            .join(ShipPointFrom, Barcode.PointFrom == ShipPointFrom.ID, isouter=True)
            .join(ShipPointTo, Barcode.PointTo == ShipPointTo.ID, isouter=True)
            .join(
                TrackSummary,
                Barcode.ID == TrackSummary.BarcodeID,
            )
            .join(TrackShipHistory, TrackSummary.TrackHistoryID == TrackShipHistory.ID, isouter=True)
            .join(TrackShipStatus, TrackShipHistory.TrackStatusID == TrackShipStatus.ID, isouter=True)
            .join(TrackCODHistory, TrackSummary.TrackCODHistoryID == TrackCODHistory.ID, isouter=True)
            .join(TrackCODStatus, TrackCODHistory.TrackCODStatusID == TrackCODStatus.ID, isouter=True)
            .where(Contract2User.UserID == user_id)
        )