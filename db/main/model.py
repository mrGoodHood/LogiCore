import datetime

from pydantic import BaseModel


MAIL_TYPE_CAT = {
    4: "ONLINE_PARCEL",
    47: "PARCEL_CLASS_1",
    24: 'ONLINE_COURIER',
}


class ParsedAddressRow(BaseModel):
    id: str
    index: str
    region: str
    place: str
    street: str | None = None
    house: str | None = None