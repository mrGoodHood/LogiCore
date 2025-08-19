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