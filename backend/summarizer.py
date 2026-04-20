# backend/summarizer.py
# 역할: 자막 텍스트에서 핵심 문장 추출 및 통계 생성

import re
from collections import Counter


def split_sentences(text: str) -> list[str]:
    """마침표·줄바꿈 기준으로 문장 분리, 10자 미만 제거"""
    parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [s.strip() for s in parts if len(s.strip()) >= 10]


def score_sentences(sentences: list[str], word_freq: dict[str, int]) -> list[tuple[int, float, str]]:
    """단어 빈도 합산으로 각 문장에 중요도 점수 부여"""
    scored = []
    for i, sent in enumerate(sentences):
        words = re.findall(r'\w+', sent.lower())
        if not words:
            continue
        score = sum(word_freq.get(w, 0) for w in words) / len(words)
        scored.append((i, score, sent))
    return scored


def extract_summary(transcript: str, preprocessed_words: list[str], top_n: int = 5) -> list[str]:
    """핵심 문장 top_n개를 원문 순서대로 반환"""
    sentences = split_sentences(transcript)
    if not sentences:
        return []

    word_freq = Counter(preprocessed_words)
    scored = score_sentences(sentences, word_freq)

    # 점수 내림차순 정렬 후 top_n 선택 → 원문 순서로 재정렬
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:top_n]
    top_in_order = sorted(top, key=lambda x: x[0])
    return [sent for _, _, sent in top_in_order]


def get_stats(transcript: str, preprocessed_words: list[str]) -> dict:
    """단어 수, 문장 수, 예상 읽기 시간 반환"""
    sentences = split_sentences(transcript)
    raw_words = transcript.split()
    return {
        "word_count": len(raw_words),
        "sentence_count": len(sentences),
        "unique_keywords": len(set(preprocessed_words)),
        "read_time_min": max(1, len(raw_words) // 200),  # 분당 200단어 기준
    }
