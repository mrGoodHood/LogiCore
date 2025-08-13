from decimal import Decimal
from typing import Union

from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import FileResponse

from app.db.schema.user import User
from app.main.billing import get_contract_settings
from app.main.services.cod_registry_getter import CODRegistryGetter
from app.main.services.cod_registry_getter.schemas import CODRegistryTableRepresentation
from app.main.user import current_active_user
from app.router.dependencies import get_cod_registry_getter

router = APIRouter(prefix="/batch")


def page_validator(value: int) -> int:
    if value < 0:
        raise ValueError("Номер страницы не может быть отрицательным.")
    return value

def size_validator(value: int) -> int:
    if value <= 0:
        raise ValueError("Размер страницы не может быть меньше или равен нулю.")
    return value


@router.get(
    path="",
    summary="Получение всех партий.",
    description='''
    Возвращает все партии пользователя.
    ''',
    response_model=None,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request.",
            "model": None,
        },
    },
)
async def batch_create(
        batch_info: CreateBatchRequest,
        address_normaliser: AddressNormalizer = Depends(get_address_normaliser),
        batch_transformer: BatchTransformer = Depends(get_order_creator),
        batch_creator: BatchCreator = Depends(get_batch_creator),
) -> Union[JSONResponse, None]:
    user_id = "TODO"

    user_settings = await get_contract_settings(user_id)
    batch_info, normalise_errors = await address_normaliser.normalize(batch_info.model_dump(), user_settings)

    if normalise_errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=CreateBatchErrorResponse(
                order_errors=normalise_errors,
                batch_errors=[]
            ).model_dump()
        )

    batch_short_info_list = BatchShortInfoMapper().map_many(result)
    return GetBatchListResponse(batches=batch_short_info_list)


@router.post(
    path="",
    summary="Создание партии посылок.",
    response_model=None,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request.",
            "model": CreateBatchErrorResponse,
        },
    },
)
async def batch_create(
        batch_info: CreateBatchRequest,
        address_normaliser: AddressNormalizer = Depends(get_address_normaliser),
        batch_transformer: BatchTransformer = Depends(get_order_creator),
        batch_creator: BatchCreator = Depends(get_batch_creator),
) -> Union[JSONResponse, None]:
    user_id = "TODO"

    user_settings = await get_contract_settings(user_id)
    batch_info, normalise_errors = await address_normaliser.normalize(batch_info.model_dump(), user_settings)


    if normalise_errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=CreateBatchErrorResponse(
                order_errors=normalise_errors,
                batch_errors=[]
            ).model_dump()
        )

    batch = batch_transformer.transform(batch_info, user_settings)
    post_api = PostAPiClient(user_settings["access_token"], user_settings["auth_key"])
    batch_errors, order_errors = await batch_creator.create(user_id, post_api, batch)

    if batch_errors or order_errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=CreateBatchErrorResponse(
                order_errors=order_errors,
                batch_errors=batch_errors
            ).model_dump()
        )

    return None


@router.get(
    path="/{batch_name}/documents",
    summary="Генерация пакета документации.",
    description='''
    Генерирует и возвращает zip архив с 4-мя файлами:
    \n  - Export.xls, Export.csv — список с основными данными по заявкам в составе партии;
    \n  - F103.pdf — форма ф103 по заявкам в составе партии;
    \n  - В зависимости от типа и категории отправлений, формируется комбинация из сопроводительных документов в формате pdf (формы: f7, f112, f22).
    ''',
    response_model=None,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request.",
            "model": GetBatchDocumentsError,
        },
    },
)

async def get_documents(
        batch_name: str,
        batch_documents_getter: BatchDocumentsGetter = Depends(get_batch_documents_getter),
) -> Union[Response]:
    user_id = "fd42a0b9-66f7-402c-ab04-51fbe09bce16"
    result = await batch_documents_getter.get(user_id, batch_name)

    if isinstance(result, GetBatchDocumentsError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=result.model_dump()
        )

    headers = {"Content-Disposition": f"attachment; filename=doc_{batch_name}.zip"}
    return Response(result, headers=headers, media_type="application/zip")
