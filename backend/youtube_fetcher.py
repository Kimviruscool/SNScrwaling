# backend/youtube_fetcher.py
# 역할: 유튜브 URL에서 video ID, 자막, 메타데이터 가져오기

import re
import httpx
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """URL에서 11자리 유튜브 video ID 추출"""
    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("유효한 유튜브 URL이 아닙니다.")


def fetch_transcript(video_id: str) -> str:
    """
    자막 텍스트 가져오기 (youtube-transcript-api 1.2.x 대응).
    api.fetch()  → 언어 지정 자막 가져오기
    api.list()   → 사용 가능한 자막 목록
    실패 시 ValueError 발생 → api.py 에서 400으로 처리
    """
    api = YouTubeTranscriptApi()

    def _join(segments) -> str:
        return " ".join(
            seg.text if hasattr(seg, "text") else seg["text"]
            for seg in segments
        )

    # 1차: 한국어/영어 지정
    try:
        return _join(api.fetch(video_id, languages=["ko", "en"]))
    except Exception:
        pass

    # 2차: 사용 가능한 모든 자막 순회
    try:
        for transcript in api.list(video_id):
            try:
                return _join(api.fetch(video_id, languages=[transcript.language_code]))
            except Exception:
                continue
    except Exception as e:
        raise ValueError(f"자막 수집 실패: {e}")

    raise ValueError("사용 가능한 자막을 찾지 못했습니다. 자막이 없거나 비활성화된 영상입니다.")


async def fetch_metadata(video_id: str) -> dict:
    """유튜브 페이지 스크래핑으로 영상 제목 가져오기"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, headers=headers, timeout=10.0)

    match = re.search(r'"title":"([^"]+)"', resp.text)
    title = match.group(1).replace("\\u0026", "&") if match else "제목 없음"

    return {"title": title, "video_id": video_id}
