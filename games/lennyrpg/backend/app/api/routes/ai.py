from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class GenerateQuestionsRequest(BaseModel):
    guest_name: str
    transcript: str
    num_questions: int = 5


class QuestionGen(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    difficulty: str
    topic: str


@router.post("/generate/questions")
async def generate_questions(request: GenerateQuestionsRequest) -> List[QuestionGen]:
    """
    使用 tiny_agents 生成问答
    TODO: 集成 tiny_agents
    """
    # 临时: 返回示例数据
    sample_questions = [
        QuestionGen(
            question=f"What is {request.guest_name}'s best advice for product growth?",
            options=[
                "A. Focus on user feedback",
                "B. Ignore competitors",
                "C. Copy others",
                "D. Spend more on ads"
            ],
            correct_answer=0,
            difficulty="medium",
            topic="product"
        ),
        QuestionGen(
            question=f"How does {request.guest_name} approach hiring?",
            options=[
                "A. Hire fast",
                "B. Hire slow, fire fast",
                "C. Only hire friends",
                "D. Outsource everything"
            ],
            correct_answer=1,
            difficulty="medium",
            topic="hiring"
        )
    ]

    return sample_questions
