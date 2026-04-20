# backend/schemas.py
# 역할: API 요청/응답 데이터 구조 정의

from pydantic import BaseModel, HttpUrl


class YoutubeRequest(BaseModel):
    url: str          # 유튜브 영상 URL
    top_n: int = 10   # 추출할 키워드 수 (기본값 10개)


class KeywordItem(BaseModel):
    keyword: str
    score: float


class AnalysisResponse(BaseModel):
    title: str
    video_id: str
    keywords: list[KeywordItem]
    transcript_preview: str  # 자막 앞부분 200자
