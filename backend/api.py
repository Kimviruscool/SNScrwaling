# backend/api.py
# 역할: 각 모듈을 연결해서 /analyze 엔드포인트 제공

from fastapi import APIRouter, HTTPException

from backend.schemas import YoutubeRequest, AnalysisResponse, ContentStats
from backend.youtube_fetcher import extract_video_id, fetch_transcript, fetch_metadata
from backend.text_processor import preprocess
from backend.keyword_extractor import extract_keywords
from backend.summarizer import extract_summary, get_stats

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_youtube(req: YoutubeRequest):
    # 1. URL → video ID
    try:
        video_id = extract_video_id(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. 메타데이터 + 자막 수집
    metadata = await fetch_metadata(video_id)
    try:
        transcript = fetch_transcript(video_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. 전처리
    words = preprocess(transcript)

    # 4. 키워드 추출
    keywords = extract_keywords(words, req.top_n)

    # 5. 핵심 요약 + 통계
    summary = extract_summary(transcript, words, top_n=5)
    raw_stats = get_stats(transcript, words)

    return AnalysisResponse(
        title=metadata["title"],
        video_id=video_id,
        keywords=keywords,
        summary=summary,
        stats=ContentStats(**raw_stats),
        transcript_preview=transcript[:300] + "...",
    )
