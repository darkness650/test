from fastapi import APIRouter
from backed_end.pojo.question import question
from backed_end.service.ai_service import aiResponse
router = APIRouter(prefix="/ai", tags=["ai"])
@router.post("")
async def ai(question: question):
    result = aiResponse(question)
    return {"result": result}