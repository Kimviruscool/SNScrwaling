# backend/api.py
# 역할: 각 모듈을 연결해서 /analyze 엔드포인트 제공

from fastapi import APIRouter, HTTPException

from backend.schemas import YoutubeRequest, AnalysisResponse, ContentStats, GeminiAnalysis
from backend.youtube_fetcher import extract_video_id, fetch_transcript, fetch_metadata
from backend.text_processor import preprocess
from backend.keyword_extractor import extract_keywords
from backend.summarizer import get_stats
from backend.gemini_summarizer import analyze as gemini_analyze

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

    # 3. 전처리 + 키워드 추출
    words    = preprocess(transcript)
    keywords = extract_keywords(words, req.top_n)

    # 4. 통계
    raw_stats = get_stats(transcript, words)

    # 5. Gemini AI 핵심 분석
    try:
        gemini_result = gemini_analyze(transcript, metadata["title"])
    except Exception as e:
        # Gemini 실패 시 빈 값으로 대체 (나머지 결과는 정상 반환)
        gemini_result = {"one_line": f"AI 분석 실패: {e}", "points": [], "topics": []}

    return AnalysisResponse(
        title=metadata["title"],
        video_id=video_id,
        keywords=keywords,
        gemini=GeminiAnalysis(**gemini_result),
        stats=ContentStats(**raw_stats),
        transcript_preview=transcript[:300] + "...",
    )
