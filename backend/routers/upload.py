from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식입니다: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다.")

    # TODO Phase 2: OCR 서비스 연동
    return {"message": "업로드 성공 (OCR 미구현)", "filename": file.filename, "size": len(contents)}
