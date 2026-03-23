from fastapi import APIRouter
from pydantic import BaseModel, Field

from chatbot.faq_data import FAQ_ITEMS
from chatbot.service import get_support_answer

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatbotQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)


class ChatbotQueryResponse(BaseModel):
    matched: bool
    question: str
    answer: str


@router.get("/faqs")
def list_employee_support_faqs() -> dict[str, list[dict[str, str]]]:
    faqs = [{"question": item["question"], "answer": item["answer"]} for item in FAQ_ITEMS]
    return {"faqs": faqs}


@router.post("/support", response_model=ChatbotQueryResponse)
def employee_support_chatbot(payload: ChatbotQueryRequest) -> ChatbotQueryResponse:
    result = get_support_answer(payload.query)
    return ChatbotQueryResponse(**result)
