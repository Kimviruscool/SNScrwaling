# backend/schemas.py
# 역할: API 요청/응답 데이터 구조 정의

from pydantic import BaseModel


class YoutubeRequest(BaseModel):
    url: str
    top_n: int = 10


class KeywordItem(BaseModel):
    keyword: str
    score: float


class ContentStats(BaseModel):
    word_count: int
    sentence_count: int
    unique_keywords: int
    read_time_min: int


class AnalysisResponse(BaseModel):
    title: str
    video_id: str
    keywords: list[KeywordItem]
    summary: list[str]
    stats: ContentStats
    transcript_preview: str
