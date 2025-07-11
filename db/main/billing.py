from random import randint
from db.schema.engine import async_session_maker


async def get_new_acc_number():
    return str(randint(1000000, 9999999))


async def get_acc_balance(user_id):
    async with async_session_maker() as session:
        statement = select(Contract.ID, Contract.Number, Contract.Balance).join(
            Contract2User, Contract.ID == Contract2User.ContractID
        ).where(
            Contract2User.UserID == user_id
        )
        result = await session.execute(statement)
        acc_id, acc_num, acc_balance = result.fetchone()
        return acc_id, acc_num, acc_balance
