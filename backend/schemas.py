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


class GeminiAnalysis(BaseModel):
    one_line: str        # 한 줄 요약
    points: list[str]    # 핵심 포인트 목록
    topics: list[str]    # 주제어 태그


class AnalysisResponse(BaseModel):
    title: str
    video_id: str
    keywords: list[KeywordItem]
    gemini: GeminiAnalysis
    stats: ContentStats
    transcript_preview: str
