from fastapi import APIRouter, HTTPException
from app.models.schemas import Player, Guest, Question, BattleRequest, BattleResponse, CaptureRequest
from app.supabase_client import get_supabase
import random
import uuid
from typing import List

router = APIRouter()


@router.post("/register")
def register_player() -> Player:
    """注册新玩家"""
    supabase = get_supabase()
    anon_id = str(uuid.uuid4())

    player_data = {
        "anon_id": anon_id,
        "level": 1,
        "xp": 0,
        "hp": 100,
        "max_hp": 100,
        "attack": 10,
        "gold": 100,
        "current_region_id": "grasslands"
    }

    supabase.table("anonymous_players").insert(player_data).execute()

    # 初始化排行榜
    supabase.table("leaderboard").insert({
        "anon_id": anon_id,
        "username": f"Player_{anon_id[:6]}",
        "total_captures": 0,
        "max_level": 1,
        "win_streak": 0
    }).execute()

    return Player(**player_data)


@router.get("/player/{anon_id}")
def get_player(anon_id: str) -> Player:
    """获取玩家信息"""
    supabase = get_supabase()
    result = supabase.table("anonymous_players").select("*").eq("anon_id", anon_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Player not found")

    return Player(**result.data[0])


@router.get("/guests")
def get_guests(region: str = "grasslands") -> List[Guest]:
    """获取指定区域的嘉宾列表"""
    supabase = get_supabase()
    result = supabase.table("guests").select("*").limit(10).execute()

    return [Guest(**g) for g in result.data]


@router.get("/guest/{guest_id}")
def get_guest(guest_id: str) -> Guest:
    """获取单个嘉宾信息"""
    supabase = get_supabase()
    result = supabase.table("guests").select("*").eq("id", guest_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Guest not found")

    return Guest(**result.data[0])


@router.get("/questions/{guest_id}")
def get_questions(guest_id: str) -> List[Question]:
    """获取嘉宾的问答"""
    supabase = get_supabase()
    result = supabase.table("questions").select("*").eq("guest_id", guest_id).execute()

    questions = []
    for q in result.data:
        questions.append(Question(
            id=q["id"],
            guest_id=q["guest_id"],
            question=q["question"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            difficulty=q.get("difficulty", "medium"),
            topic=q.get("topic")
        ))

    # 随机选择3-5题
    random.shuffle(questions)
    return questions[:4]


@router.post("/battle")
def battle_answer(request: BattleRequest) -> BattleResponse:
    """处理战斗答题"""
    supabase = get_supabase()

    # 获取玩家和嘉宾信息
    player_result = supabase.table("anonymous_players").select("*").eq("anon_id", request.anon_id).execute()
    guest_result = supabase.table("guests").select("*").eq("id", request.guest_id).execute()

    if not player_result.data or not guest_result.data:
        raise HTTPException(status_code=404, detail="Player or guest not found")

    player = player_result.data[0]
    guest = guest_result.data[0]

    # 获取当前问题
    questions_result = supabase.table("questions").select("*").eq("guest_id", request.guest_id).execute()
    if not questions_result.data:
        raise HTTPException(status_code=400, detail="No questions available")

    question = questions_result.data[0]
    is_correct = request.answer == question["correct_answer"]

    # 计算伤害
    if is_correct:
        enemy_damage = int(20 + player["attack"] * 0.5)
        player_damage = 0
    else:
        enemy_damage = 0
        player_damage = 15

    enemy_hp = guest["hp"] - enemy_damage
    player_hp = player["hp"] - player_damage

    battle_over = enemy_hp <= 0 or player_hp <= 0
    victory = enemy_hp <= 0 if battle_over else None

    return BattleResponse(
        correct=is_correct,
        player_damage=player_damage,
        enemy_damage=enemy_damage,
        player_hp=max(0, player_hp),
        enemy_hp=max(0, enemy_hp),
        battle_over=battle_over,
        victory=victory
    )


@router.post("/capture")
def capture_guest(request: CaptureRequest) -> dict:
    """捕获嘉宾"""
    if not request.success:
        return {"success": False, "message": "Capture failed"}

    supabase = get_supabase()

    supabase.table("captures").insert({
        "anon_id": request.anon_id,
        "guest_id": request.guest_id,
        "battle_score": 0
    }).execute()

    # 更新玩家金币
    supabase.table("anonymous_players").update({
        "gold": 50
    }).eq("anon_id", request.anon_id).execute()

    # 更新排行榜
    supabase.table("leaderboard").update({
        "total_captures": 1
    }).eq("anon_id", request.anon_id).execute()

    return {"success": True, "message": "Guest captured!"}
