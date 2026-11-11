from fastapi import APIRouter

router = APIRouter(tags=["health"])


# Estado de la API
@router.get("/health")
def revisar_estado() -> dict[str, str]:
    return {"estado": "ok"}
