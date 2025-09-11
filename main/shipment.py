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