from fastapi import APIRouter

router = APIRouter()


def build_health_payload() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "api",
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    return build_health_payload()
