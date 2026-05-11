from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter()


@router.get("/expenses")
def get_expenses(from_date: Optional[str] = None, to_date: Optional[str] = None):
    # TODO Phase 3: storage_service 연동
    return []


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    # TODO Phase 3: storage_service 연동
    raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")


@router.put("/expenses/{expense_id}")
def update_expense(expense_id: str, body: dict):
    # TODO Phase 3: storage_service 연동
    raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
