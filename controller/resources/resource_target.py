from typing import List
from fastapi import APIRouter


router_target = APIRouter()


# Load targets
LIST_OF_URLS = []
with open('/app/targets.txt') as f:
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if len(l) > 0]
    LIST_OF_URLS.extend(lines)


@router_target.get("/targets", response_model=List[str])
def targets() -> List[str]:
    return LIST_OF_URLS
