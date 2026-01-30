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

