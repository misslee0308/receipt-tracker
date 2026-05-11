from fastapi import APIRouter
from typing import Optional

router = APIRouter()


@router.get("/summary")
def get_summary(month: Optional[str] = None):
    # TODO Phase 3: storage_service 연동
    return {"total_amount": 0, "this_month_amount": 0, "category_summary": []}
