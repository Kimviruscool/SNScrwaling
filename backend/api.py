# backend/api.py
from fastapi import APIRouter
# 📌 app 폴더 대신 backend 폴더에서 임포트합니다.
from backend.schemas import SummaryRequest
from backend.services import fetch_sns_data

router = APIRouter()


@router.post("/generate")
async def generate_summary(req: SummaryRequest):
    try:
        raw_sns_data = await fetch_sns_data(req.category, req.url)
        extracted_text_preview = raw_sns_data["content"][:15] + "..."

        return {
            "success": True,
            "data": {
                "title": f"요약: {extracted_text_preview}",
                "url": req.url,
                "status": "Completed",
                "time": "Just now",
                "tags": [req.category, "Scraped"]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}