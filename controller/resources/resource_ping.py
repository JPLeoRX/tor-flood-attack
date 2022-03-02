from fastapi import APIRouter


router_ping = APIRouter()


@router_ping.get("/ping", response_model=bool)
def ping() -> bool:
    return True
