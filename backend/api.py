# backend/api.py
# 역할: 각 모듈을 연결해서 /analyze 엔드포인트 제공

from fastapi import APIRouter, HTTPException

from backend.schemas import YoutubeRequest, AnalysisResponse
from backend.youtube_fetcher import extract_video_id, fetch_transcript, fetch_metadata
from backend.text_processor import preprocess
from backend.keyword_extractor import extract_keywords

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_youtube(req: YoutubeRequest):
    # 1. URL → video ID
    try:
        video_id = extract_video_id(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. 메타데이터(제목) + 자막 병렬 수집
    metadata = await fetch_metadata(video_id)
    transcript = fetch_transcript(video_id)

    if not transcript:
        raise HTTPException(status_code=400, detail="자막을 가져올 수 없습니다. 자막이 없는 영상일 수 있습니다.")

    # 3. 전처리 → 키워드 추출
    words = preprocess(transcript)
    keywords = extract_keywords(words, req.top_n)

    return AnalysisResponse(
        title=metadata["title"],
        video_id=video_id,
        keywords=keywords,
        transcript_preview=transcript[:200] + "...",
    )
