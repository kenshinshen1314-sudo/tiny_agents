from fastapi import APIRouter, HTTPException
from app.models.team import TeamTemplate
from app.services.template_service import TemplateService
from typing import List

router = APIRouter(prefix="/api/templates", tags=["templates"])
template_service = TemplateService()

@router.get("/", response_model=List[TeamTemplate])
async def list_templates():
    return template_service.list_templates()

@router.get("/{template_id}", response_model=TeamTemplate)
async def get_template(template_id: str):
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/analyze")
async def analyze_input(user_input: str):
    return await template_service.analyze_and_recommend(user_input)