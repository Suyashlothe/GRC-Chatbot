from fastapi import APIRouter

from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    result = await chat_service.process_message(
        request.message
    )

    return ChatResponse(
        response=str(result)
    )