from fastapi import APIRouter

router = APIRouter()

# Placeholder routes - will be implemented in future phases

@router.get("/")
def games_root():
    return {"message": "Games API"}