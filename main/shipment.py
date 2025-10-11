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

    acc_id, acc_num, acc_balance = await get_acc_balance(user_id)

    if not await check_balance_fee(acc_id, Decimal(total_cost) / 100):
        return {'errors': {'detail': 'Недостаточно средств'}}

    body = json.dumps(new_orders)
    res = await api.order_create(body)
    ship_date = datetime.strptime(orders.orders.shipping_date, "%Y-%m-%d").date()
    if res.get('result-ids'):
        batches = await api.batch_create(res.get('result-ids'), ship_date)
        for batch in batches['batches']:
            batch_name = batch['batch-name']
            batch_id = await save_batch(
                acc_id,
                user_id,
                settings,
                batch_name
            )
            await save_shipment(
                acc_id,
                user_id,
                settings,
                batch_id,
                batch_name,
                res.get('result-ids')
            )

            await charge_order_fee(
                acc_id,
                user_id,
                batch_name,
                Decimal(total_cost) / 100
            )


async def get_batch_list(user_id, page: str = "", size: str = ""):
    settings = await get_contract_settings(user_id)

    api = PostAPiClient(settings['access_token'], settings['auth_key'])
    return await api.get_batch_list(page=page, size=size)


async def get_batch_documents(user_id, bath_name):
    settings = await get_contract_settings(user_id)
    api = PostAPiClient(settings['access_token'], settings['auth_key'])
    return await api.get_batch_documents(bath_name, settings['print_type'])


async def handle_xls_file(user_id, file):

    data = parse_xls(file)

    address_list = AddressList(
        address_list=[
            AddressRow(
                rownum=row['row_num'],
                address=row['ADDRESSLINE']
            ) for row in data
        ]
    )