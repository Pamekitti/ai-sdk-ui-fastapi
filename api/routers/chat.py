import json
from typing import List
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..services.openai import OpenAIService
from ..utils.prompt import ClientMessage, convert_to_openai_messages
from ..utils.tools import get_current_weather, generate_mock_chart

router = APIRouter()

class ChatRequest(BaseModel):
    messages: List[ClientMessage]

available_tools = {
    "get_current_weather": get_current_weather,
    "generate_mock_chart": generate_mock_chart,
}

@router.post("/chat_streaming")
async def handle_chat_streaming(request: ChatRequest, protocol: str = Query('data')):
    """
    Handle streaming chat requests
    """
    
    messages = request.messages
    openai_messages = convert_to_openai_messages(messages)

    response = StreamingResponse(
        OpenAIService.stream_text(openai_messages, protocol)
    )
    response.headers['x-vercel-ai-data-stream'] = 'v1'
    return response

@router.post("/chat")
async def handle_chat(request: ChatRequest):
    """
    Handle regular chat requests
    """
    # Mock response that matches the Message interface
    return {} 