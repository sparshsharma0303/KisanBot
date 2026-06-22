import sys
from fastapi import APIRouter, HTTPException
from src.logger import logging
from src.exceptions import KisanBotException
from src.components.agent import build_agent
from src.api.models import QuestionRequest, AnswerResponse, SourceChunk

router = APIRouter()
agent = build_agent()

@router.post("/ask", response_model = AnswerResponse)
def ask_question(request: QuestionRequest):
    try:
        logging.info(f"received question: {request.question}")

        result = agent.invoke({
            "question": request.question,
            "chunks":[],
            "answer":""
        })

        sources = [
            SourceChunk(content = chunk.page_content[:200])
            for chunk in result["chunks"]
        ]
        return AnswerResponse(
            question = request.question,
            answer = result['answer'],
            sources = sources
        )
    except Exception as e:
        logging.error(f"error processing question: {e}")
        raise KisanBotException(e,sys)
    
