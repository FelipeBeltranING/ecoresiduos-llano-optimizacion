from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def revisar_estado() -> dict[str, str]:
    return {"estado": "ok"}
