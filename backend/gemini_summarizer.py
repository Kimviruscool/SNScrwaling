# backend/gemini_summarizer.py
# 역할: Gemini API로 자막 텍스트를 분석해 핵심 요약 반환

import os
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL  = "gemini-2.5-flash"

_PROMPT_TEMPLATE = """
다음은 YouTube 영상 제목 "{title}"의 자막 텍스트입니다.

[자막]
{transcript}

아래 형식을 정확히 지켜 한국어로 분석해주세요.

[한줄요약]
영상 전체를 한 문장으로 요약

[핵심포인트]
1. 첫 번째 핵심 내용
2. 두 번째 핵심 내용
3. 세 번째 핵심 내용
4. 네 번째 핵심 내용
5. 다섯 번째 핵심 내용

[주제어]
키워드1, 키워드2, 키워드3, 키워드4, 키워드5
"""


def analyze(transcript: str, title: str) -> dict:
    """
    Gemini API 호출 후 구조화된 분석 결과 반환.
    Returns: { "one_line": str, "points": list[str], "topics": list[str] }
    """
    clipped = transcript[:4000]
    prompt  = _PROMPT_TEMPLATE.format(title=title, transcript=clipped)

    response = _client.models.generate_content(model=_MODEL, contents=prompt)
    return _parse(response.text)


def _parse(text: str) -> dict:
    """Gemini 응답 텍스트 → 딕셔너리"""
    result = {"one_line": "", "points": [], "topics": []}

    m = re.search(r"\[한줄요약\]\s*(.+?)(?=\[|$)", text, re.S)
    if m:
        result["one_line"] = m.group(1).strip().split("\n")[0].strip()

    m = re.search(r"\[핵심포인트\]\s*(.+?)(?=\[|$)", text, re.S)
    if m:
        lines = m.group(1).strip().split("\n")
        result["points"] = [
            re.sub(r"^\d+\.\s*", "", l).strip()
            for l in lines
            if re.match(r"^\d+\.", l.strip())
        ]

    m = re.search(r"\[주제어\]\s*(.+?)(?=\[|$)", text, re.S)
    if m:
        raw = m.group(1).strip().split("\n")[0]
        result["topics"] = [t.strip() for t in raw.split(",") if t.strip()]

    return result
