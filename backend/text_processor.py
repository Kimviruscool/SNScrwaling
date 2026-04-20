# backend/text_processor.py
# 역할: 텍스트 정제, 토큰화, 불용어 제거

import re

# 한국어·영어 불용어 목록
_KO_STOPWORDS = {
    "이", "가", "은", "는", "을", "를", "의", "에", "와", "과",
    "도", "로", "으로", "그", "저", "것", "수", "있", "하", "않",
    "더", "만", "도", "에서", "이다", "있다", "하다", "되다", "그리고",
    "그래서", "하지만", "그런데", "또는", "그냥", "아주", "너무",
}
_EN_STOPWORDS = {
    "the", "a", "an", "is", "it", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "i", "you", "we", "they", "this",
    "that", "was", "are", "be", "have", "has", "do", "did", "not",
    "with", "as", "by", "from", "so", "if", "will", "can", "just",
}
_STOPWORDS = _KO_STOPWORDS | _EN_STOPWORDS


def clean_text(text: str) -> str:
    """특수문자 제거 및 공백 정리 (한글·영문·숫자만 유지)"""
    text = re.sub(r"[^\w\s가-힣]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    """공백 기준 분리 후 길이 2 이상 단어만 반환"""
    return [w for w in text.split() if len(w) >= 2]


def remove_stopwords(words: list[str]) -> list[str]:
    """불용어 제거"""
    return [w for w in words if w.lower() not in _STOPWORDS]


def preprocess(text: str) -> list[str]:
    """clean → tokenize → remove_stopwords 순서로 전처리"""
    return remove_stopwords(tokenize(clean_text(text)))
