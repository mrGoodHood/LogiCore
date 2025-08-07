from fastapi import APIRouter

router = APIRouter(prefix="/batch")


def page_validator(value: int) -> int:
    if value < 0:
        raise ValueError("Номер страницы не может быть отрицательным.")
    return value

def size_validator(value: int) -> int:
    if value <= 0:
        raise ValueError("Размер страницы не может быть меньше или равен нулю.")
    return value