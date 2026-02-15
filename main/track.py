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
)
