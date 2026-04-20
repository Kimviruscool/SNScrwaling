# backend/keyword_extractor.py
# 역할: 전처리된 단어 목록에서 빈도 기반 키워드 추출

from collections import Counter


def compute_frequency(words: list[str]) -> dict[str, float]:
    """단어 목록에서 정규화된 빈도(TF) 계산"""
    if not words:
        return {}
    total = len(words)
    return {word: count / total for word, count in Counter(words).items()}


def extract_keywords(words: list[str], top_n: int = 10) -> list[dict]:
    """빈도 높은 순으로 top_n개 키워드 반환"""
    freq = compute_frequency(words)
    ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [{"keyword": w, "score": round(s, 4)} for w, s in ranked[:top_n]]
