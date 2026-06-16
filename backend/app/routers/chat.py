"""AI data assistant chat routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_user_dataset
from app.models.dataset import Dataset
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_assistant import process_chat_message
from app.utils.file_handler import load_dataframe

router = APIRouter(prefix="/chat", tags=["AI Assistant"])


@router.post("/{dataset_id}", response_model=ChatResponse)
async def chat_with_dataset(
    request: ChatRequest,
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
):
    df = load_dataframe(dataset.file_path, dataset.file_type)
    insights = dataset.insights_cache or (dataset.analysis_cache or {}).get("insights")
    reply, suggestions = process_chat_message(
        request.message,
        df,
        insights=insights,
        quality_score=dataset.data_quality_score,
    )
    return ChatResponse(reply=reply, suggestions=suggestions)
