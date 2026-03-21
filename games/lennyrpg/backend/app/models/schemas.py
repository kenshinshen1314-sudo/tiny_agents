from pydantic import BaseModel, Field
from typing import List, Optional


class Player(BaseModel):
    anon_id: str
    level: int = 1
    xp: int = 0
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    gold: int = 100
    current_region_id: str = "grasslands"


class Guest(BaseModel):
    id: str
    name: str
    avatar_url: Optional[str]
    type: str
    rarity: str
    bio: Optional[str]
    hp: int = 100
    attack: int = 10
    xp_reward: int = 50
    guest_number: int


class Question(BaseModel):
    id: str
    guest_id: str
    question: str
    options: List[str]
    correct_answer: int
    difficulty: str = "medium"
    topic: Optional[str]


class BattleRequest(BaseModel):
    anon_id: str
    guest_id: str
    answer: int = Field(ge=0, le=3, description="Answer index (0-3)")


class BattleResponse(BaseModel):
    correct: bool
    player_damage: int
    enemy_damage: int
    player_hp: int
    enemy_hp: int
    battle_over: bool
    victory: Optional[bool] = None


class CaptureRequest(BaseModel):
    anon_id: str
    guest_id: str
    success: bool
    battle_score: Optional[int] = 0


class CaptureResponse(BaseModel):
    success: bool
    message: str
    guest_name: Optional[str] = None
