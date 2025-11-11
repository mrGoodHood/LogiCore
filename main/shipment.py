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

    settings = await get_contract_settings(user_id)

    api = PostAPiClient(settings['access_token'], settings['auth_key'])

    address_validation = await api.norm_address(address_list.address_list)
    address_data = {address['id']: address for address in address_validation}

    for item in data:
        item['MAILTYPE'] = MAIL_TYPE_CAT[item['MAILTYPE']]
        item['MASS'] = int(Decimal(item['MASS']) * 1000)
        item['address_val'] = address_data.get(item['row_num'])
        mail_cat = "ORDINARY"
        if Decimal(item['PAYMENT']) * 100 > 0:
            mail_cat = "WITH_DECLARED_VALUE_AND_CASH_ON_DELIVERY"
        elif Decimal(item['VALUE']) * 100 > 0:
            mail_cat = "WITH_DECLARED_VALUE"
        index = item['address_val'].get('index')
        item['cost'] = None
        if index:
            cost_request = {
                'declared-value': item['VALUE'],
                'index-to': index,
                'index-from': settings['shipping_point'],
                "mass": item['MASS'],
                "mail-category": mail_cat,
                "mail-type": item['MAILTYPE'],
            }
            cost = await api.get_tarif(cost_request)
            value = cost.get('total-rate')
            if value:
                item['cost'] = int(value)
        item['address_val'] = address_data.get(item['row_num'])

    return {
        "data": data,
    }


async def save_batch(acc_id, user_id, settings, batch_name):
    api = PostAPiClient(settings['access_token'], settings['auth_key'])
    batch_data = await api.get_batch(batch_name)

    batch_rate = BatchModelRate(
        shipment_avia_rate_sum=batch_data['shipment-avia-rate-sum'],
        shipment_avia_rate_vat_sum=batch_data['shipment-avia-rate-vat-sum'],
        shipment_completeness_checking_rate_sum=batch_data['shipment-completeness-checking-rate-sum'],
        shipment_completeness_checking_rate_vat_sum=batch_data['shipment-completeness-checking-rate-vat-sum'],
        shipment_contents_checking_rate_sum=batch_data['shipment-contents-checking-rate-sum'],
        shipment_contents_checking_rate_vat_sum=batch_data['shipment-contents-checking-rate-vat-sum'],
        shipment_functionality_checking_rate_sum=batch_data['shipment-functionality-checking-rate-sum'],
        shipment_functionality_checking_rate_vat_sum=batch_data['shipment-functionality-checking-rate-vat-sum'],
        shipment_ground_rate_sum=batch_data['shipment-ground-rate-sum'],
        shipment_ground_rate_vat_sum=batch_data['shipment-ground-rate-vat-sum'],
        shipment_insure_rate_sum=batch_data['shipment-insure-rate-sum'],
        shipment_insure_rate_vat_sum=batch_data['shipment-insure-rate-vat-sum'],
        shipment_inventory_rate_sum=batch_data['shipment-inventory-rate-sum'],
        shipment_inventory_rate_vat_sum=batch_data['shipment-inventory-rate-vat-sum'],
        shipment_mass_rate_sum=batch_data['shipment-mass-rate-sum'],
        shipment_mass_rate_vat_sum=batch_data['shipment-mass-rate-vat-sum'],
        shipment_notice_rate_sum=batch_data['shipment-notice-rate-sum'],
        shipment_notice_rate_vat_sum=batch_data['shipment-notice-rate-vat-sum'],
        shipment_partial_redemption_rate_sum=batch_data.get('shipment-partial-redemption-rate-sum', 0),
        shipment_partial_redemption_rate_vat_sum=batch_data.get('shipment-partial-redemption-rate-vat-sum', 0),
        shipment_pre_postal_preparation_rate_sum=batch_data['shipment-pre-postal-preparation-rate-sum'],
        shipment_pre_postal_preparation_rate_vat_sum=batch_data['shipment-pre-postal-preparation-rate-vat-sum'],
        shipment_sms_notice_rate_sum=batch_data['shipment-sms-notice-rate-sum'],
        shipment_sms_notice_rate_vat_sum=batch_data['shipment-sms-notice-rate-vat-sum'],
        shipment_with_fitting_rate_sum=batch_data['shipment-with-fitting-rate-sum'],
        shipment_with_fitting_rate_vat_sum=batch_data['shipment-with-fitting-rate-vat-sum'],
    )

    batch = BatchModel(
        batch_name=batch_data['batch-name'],
        batch_category=batch_data['mail-category'],
        batch_status=batch_data['batch-status'],
        batch_status_date=datetime.strptime(batch_data['batch-status-date'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        batch_sent_date=datetime.strptime(batch_data['list-number-date'], '%Y-%m-%d').date(),
        postoffice_code=batch_data['postoffice-code'],
        postoffice_name=batch_data['postoffice-name'],
        postoffice_address=batch_data.get('postoffice-address'),
        mass=batch_data['shipment-mass'],
        shipment_count=batch_data['shipment-count'],
        rate=batch_rate
    )
    batch_id = await add_batch(acc_id, user_id, batch)
    await add_rate(batch_id, batch_rate)
    return batch_id


async def add_batch(contract_id, user_id, batch_data):
    async with async_session_maker() as session, session.begin():
        obj = Batch(
            ContractID=contract_id,
            UserID=user_id,
            BatchName=batch_data.batch_name,
            BatchCategory=batch_data.batch_category,
            BatchStatus=batch_data.batch_status,
            BatchStatusDate=batch_data.batch_status_date,
            BatchSentDate=batch_data.batch_sent_date,
            PostOfficeCode=batch_data.postoffice_code,
            PostOfficeName=batch_data.postoffice_name,
            PostOfficeAddress=batch_data.postoffice_address,
            Mass=batch_data.mass,
            ShipmentCount=batch_data.shipment_count,
            TotalRate=batch_data.rate.get_rate(),
            TotalRateVat=batch_data.rate.get_rate_vat(),
        )

async def get_rate_type(rate_name):
    async with async_session_maker() as session, session.begin():
        stmt = select(RateType.ID).where(RateType.Name==rate_name)
        result = await session.execute(stmt)
        rate_id = result.fetchone()
        if rate_id:
            return rate_id[0]
        obj = RateType(
            Name=rate_name
        )
        session.add(obj)
        await session.commit()
        return obj.ID


async def add_rate(batch_id, batch_rate, barcode_id=None):
    async with async_session_maker() as session, session.begin():
        for rate in batch_rate.model_fields:
            value = getattr(batch_rate, rate)
            if value:
                obj = Rate(
                    BatchID=batch_id,
                    BarcodeID=barcode_id,
                    BatchRateType=await get_rate_type(rate),
                    BatchRateValue=value
                )
                session.add(obj)
        await session.commit()


async def save_shipment(acc_id, user_id, settings, batch_id, batch_name, shipment_ids=None):
    api = PostAPiClient(settings['access_token'], settings['auth_key'])
    shipments = await api.get_batch_shipments(batch_name)
    for shipment in shipments:
        shipment_rate = ShipmentRate(
            ground_rate=shipment['ground-rate'],
            ground_rate_with_vat=shipment['ground-rate-with-vat'],
            ground_rate_wo_vat=shipment['ground-rate-wo-vat'],
            insr_rate=shipment['insr-rate'],
            insr_rate_with_vat=shipment['insr-rate-with-vat'],
            insr_rate_wo_vat=shipment['insr-rate-wo-vat'],
            mass_rate=shipment['mass-rate'],
            mass_rate_with_vat=shipment['mass-rate-with-vat'],
            mass_rate_wo_vat=shipment['mass-rate-wo-vat'],
            total_rate_wo_vat=shipment['total-rate-wo-vat'],
            total_vat=shipment['total-vat'],
        )

        ship_point_from_id = await get_or_create_ship_point(str(shipment["index-from"]), settings)
        ship_point_to_id = await get_or_create_ship_point(str(shipment["index-to"]), settings)

        shipment_model = ShipmentModel(
            ext_id=shipment['id'],
            barcode=shipment['barcode'],
            order_num=shipment['order-num'],
            mail_type=shipment['mail-type'],
            mail_cat=shipment['mail-category'],
            declared_values=shipment.get('declared-values'),
            dimensions=shipment.get('dimensions'),
            delidery_time=shipment['delivery-time'] or {},
            index_from=shipment['index-from'],
            index_to=shipment['index-to'],
            point_from=ship_point_from_id,
            point_to=ship_point_to_id,
            mass=shipment['mass'],
            shelf_life_days=shipment['shelf-life-days'],
            insure_value=shipment['insr-value'],
            cod_payment=shipment['payment'],
            rate=shipment_rate,
        )
