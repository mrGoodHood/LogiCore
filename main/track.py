class TrackSummaryFilter(StrEnum):
    IS_RETURNED = "is_returned"
    IS_HOT = "is_hot"
    IS_NOT_HOT = "is_not_hot"
    IS_HANGING = "is_hanging"


class TrackSummarySort(StrEnum):
    TRACK_STATUS = "track_status"
    BATCH_SENT_DATE = "batch_sent_date"

