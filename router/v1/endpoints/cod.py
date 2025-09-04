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


router = APIRouter(prefix="/cod")


@router.get(
    path="/registry",
    summary="Получить реестр наложенных платежей.",
    description="Получить реестр наложенных платежей",
    response_model=list[CODRegistryTableRepresentation],
)
async def get_cod_registry(
        cod_registry_getter: CODRegistryGetter = Depends(get_cod_registry_getter),
        user: User = Depends(current_active_user),
) -> Union[Response, list[CODRegistryTableRepresentation]]:
    user_settings = await get_contract_settings(user.id)
    cod_fee = user_settings.get("cod_fee")

    if not cod_fee:
        raise HTTPException(detail=f"cod_fee не определен у пользователя {user.id}", status_code=404)

    registries = await cod_registry_getter.get(user.id, Decimal(cod_fee))
    return registries


@router.get(
    path="/registry/csv",
    summary="Получить csv файл с реестром всех наложенных платежей.",
    description="Получить csv файл с реестром всех наложенных платежей",
    response_class = Response,
)
async def get_cod_registry_file(
        cod_registry_getter: CODRegistryGetter = Depends(get_cod_registry_getter),
        user: User = Depends(current_active_user),
) -> Response:
    user_settings = await get_contract_settings(user.id)
    cod_fee = user_settings.get("cod_fee")

    if not cod_fee:
        raise HTTPException(detail=f"cod_fee не определен у пользователя {user.id}", status_code=404)

    buffer = await cod_registry_getter.get_csv(user.id, Decimal(cod_fee))
    response = Response(content=buffer.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=cod_registries.csv"
    return response


@router.get(
    path="/registry/{cod_registry_id}/csv",
    summary="Получить csv файл по реестру наложенных платежей.",
    description="Получить csv файл по реестру наложенных платежей",
    response_class = Response,
)
async def get_cod_registry_file(
        cod_registry_id: int,
        cod_registry_getter: CODRegistryGetter = Depends(get_cod_registry_getter),
        user: User = Depends(current_active_user),
) -> Response:
    user_settings = await get_contract_settings(user.id)
    cod_fee = user_settings.get("cod_fee")

    if not cod_fee:
        raise HTTPException(detail=f"cod_fee не определен у пользователя {user.id}",
                            status_code=404)

    buffer = await cod_registry_getter.get_csv_by_cod_registry(
        user_id=user.id,
        cod_registry_id=cod_registry_id,
        cod_fee=Decimal(cod_fee)
    )
    response = Response(content=buffer.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=cod_registries.csv"
    return response


@router.get(
    path="/registry/dbf",
    summary="Получить dbf файл с реестром всех наложенных платежей.",
    description="Получить dbf файл с реестром всех наложенных платежей",
    response_class = FileResponse,
)
async def get_cod_registry_file(
        cod_registry_getter: CODRegistryGetter = Depends(get_cod_registry_getter),
        user: User = Depends(current_active_user),
) -> FileResponse:
    file_path = await cod_registry_getter.get_dbf(user.id)
    return FileResponse(path=file_path, media_type='application/dbf', filename=file_path.name)
