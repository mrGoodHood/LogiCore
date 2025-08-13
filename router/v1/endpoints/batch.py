from types import NoneType

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
