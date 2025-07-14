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


class ParsedAddressList(BaseModel):
    address_list: list[ParsedAddressRow] = None


class AddressRow(BaseModel):
    """Строка адреса для валидации
    """
    rownum: int
    address: str


class AddressList(BaseModel):
    """Список адресов для валидации отправляется в API https://otpravka.pochta.ru/specification#/nogroup-normalization_adress
    """
    address_list: list[AddressRow] = None


class NameRow(BaseModel):
    rownum: int
    name: str
