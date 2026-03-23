"""Simple keyword-based answer matching for EMS employee support chatbot."""

from __future__ import annotations

import re
from typing import TypedDict

from chatbot.faq_data import FAQ_ITEMS


class SupportAnswer(TypedDict):
    matched: bool
    question: str
    answer: str


def _normalize_tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return set(words)


def get_support_answer(query: str) -> SupportAnswer:
    query = (query or "").strip()
    query_tokens = _normalize_tokens(query)

    best_score = 0
    best_item = None

    for item in FAQ_ITEMS:
        keyword_tokens = set(item["keywords"])
        score = len(query_tokens.intersection(keyword_tokens))

        if score > best_score:
            best_score = score
            best_item = item

    if best_item and best_score > 0:
        return {
            "matched": True,
            "question": best_item["question"],
            "answer": best_item["answer"],
        }

    return {
        "matched": False,
        "question": "No exact FAQ match",
        "answer": (
            "I could not find an exact answer. Please share more details like module "
            "(attendance, payroll, login), date, and employee ID for support."
        ),
    }
