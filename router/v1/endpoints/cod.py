router = APIRouter(prefix="/cod")


@router.get(
    path="/registry",
    summary="Получить реестр наложенных платежей.",
    description="Получить реестр наложенных платежей",
    response_model=list[CODRegistryTableRepresentation],
)
