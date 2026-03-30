# backend/api.py
from fastapi import APIRouter
from backend.schemas import SummaryRequest
from backend.services import fetch_sns_data

router = APIRouter()


@router.post("/generate")
async def generate_summary(req: SummaryRequest):
    try:
        # 1. 방금 만든 진짜 스크래핑 함수 호출
        raw_sns_data = await fetch_sns_data(req.category, req.url)

        # 🎯 2. PyCharm 콘솔 창에 추출된 JSON 데이터 출력해서 확인하기!
        print("===== [추출된 JSON 데이터] =====")
        import json
        print(json.dumps(raw_sns_data, ensure_ascii=False, indent=2))
        print("================================")

        # 스크래핑에 실패한 경우 처리
        if "error" in raw_sns_data:
            raise Exception(raw_sns_data["error"])

        # 3. 추출한 제목을 카드의 타이틀로 사용
        extracted_title = raw_sns_data.get("extracted_title", "제목 없음")

        return {
            "success": True,
            "data": {
                "title": extracted_title[:30] + "...",  # 제목이 너무 길면 자름
                "url": req.url,
                "status": "Completed",
                "time": "Just now",
                "tags": [req.category, "Scraped"]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}