import json
from datetime import datetime
from typing import Any, Optional

from ..db.schema.shipment import Batch, Barcode, Rate, RateType, ShipPoint
from ..db.engine import async_session_maker
from sqlalchemy import select
from decimal import Decimal


async def new_batch(user_id, orders):
    new_orders = []
    total_cost = 0

    data = {num: row for num, row in enumerate(orders.orders.orders_list)}
    address_list = AddressList(
        address_list=[
            AddressRow(
                rownum=num,
                address=row.ADDRESSLINE
            ) for num, row in data.items()
        ]
    )

    settings = await get_contract_settings(user_id)

    api = PostAPiClient(settings['access_token'], settings['auth_key'])


    address_validation = await api.norm_address(address_list.address_list)
    addess_data = {address['id']: address for address in address_validation}
    for num, order in data.items():
        name_parts = str(order.ADRESAT).split(' ')
        try:
            last_name = name_parts[0]
            given_name = name_parts[1]
            middle_name = ' '.join(name_parts[2:])
        except IndexError:
            last_name = str(order.ADRESAT)
            given_name = ''
            middle_name = ''

        mail_cat = "ORDINARY"
        if float(order.PAYMENT) * 100 > 0:
            mail_cat = "WITH_DECLARED_VALUE_AND_CASH_ON_DELIVERY"
        elif float(order.VALUE) * 100 > 0:
            mail_cat = "WITH_DECLARED_VALUE"

        new_order = {
            "address-type-to": "DEFAULT",
            "given-name": given_name,
            # "recipient-name": order.ADRESAT,
            "house-to": addess_data[str(num)].get('house'),
            "index-to": addess_data[str(num)].get('index'),
            "mail-category": mail_cat,
            "mail-direct": 643,
            "mail-type": order.MAILTYPE,
            "no-return": order.NORETURN,
            "insr-value": order.VALUE * 100,
            "payment": order.PAYMENT * 100,
            "mass": str(Decimal(order.MASS)),
            "comment": order.EXTCOMMENT if order.EXTCOMMENT and len(order.EXTCOMMENT) < 200 else '',
            "sms-notice-recipient": 1 if order.SMSNOTICERECIPIENT else 0,
            "middle-name": middle_name,
            "order-num": str(order.ORDERNUM),
            "place-to": addess_data[str(num)].get('place'),
            "postoffice-code": settings['shipping_point'],
            "region-to": addess_data[str(num)].get('region'),
            "street-to": addess_data[str(num)].get('street'),
            "surname": last_name,
            "tel-address": order.TELADDRESS,
            "transport-type": "SURFACE",
        }
        cost_request = {
            'declared-value': order.VALUE,
            'index-to': addess_data[str(num)].get('index'),
            'index-from': settings['shipping_point'],
            "payment": order.PAYMENT * 100,
            "mass": order.MASS,
            "mail-category": mail_cat,
            "mail-type": order.MAILTYPE,
            "sms-notice-recipient": 1 if order.SMSNOTICERECIPIENT else 0,
        }
        cost = await api.get_tarif(cost_request)
        value = cost.get('total-rate')
        if value == 0:
            return cost
        if value:
            total_cost += int(value)
        new_orders.append(new_order)
