from db.schema.engine import async_session_maker


async def get_new_acc_number():
    return str(randint(1000000, 9999999))


async def get_acc_balance(user_id):
    async with async_session_maker() as session:
        pass
