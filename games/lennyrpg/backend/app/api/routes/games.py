from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.schemas import Player, Guest, Question, BattleRequest, BattleResponse, CaptureRequest, CaptureResponse, LevelUpRequest, LevelUpResponse
from app.supabase_client import get_supabase
import random
import uuid
from typing import List

router = APIRouter()


@router.post("/register")
def register_player() -> Player:
    """注册新玩家"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/player/{anon_id}")
def get_player(anon_id: str) -> Player:
    """获取玩家信息"""
    try:
        supabase = get_supabase()
        result = supabase.table("anonymous_players").select("*").eq("anon_id", anon_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Player not found")

        return Player(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/guests")
def get_guests(region: str = "grasslands") -> List[Guest]:
    """获取指定区域的嘉宾列表"""
    try:
        supabase = get_supabase()
        result = supabase.table("guests").select("*").eq("region_id", region).limit(10).execute()

        return [Guest(**g) for g in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/guest/{guest_id}")
def get_guest(guest_id: str) -> Guest:
    """获取单个嘉宾信息"""
    try:
        supabase = get_supabase()
        result = supabase.table("guests").select("*").eq("id", guest_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Guest not found")

        return Guest(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/questions/{guest_id}")
def get_questions(guest_id: str) -> List[Question]:
    """获取嘉宾的问答"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/battle")
def battle_answer(request: BattleRequest) -> BattleResponse:
    """处理战斗答题"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/capture")
def capture_guest(request: CaptureRequest) -> CaptureResponse:
    """捕获嘉宾"""
    try:
        supabase = get_supabase()

        if not request.success:
            return CaptureResponse(
                success=False,
                message="捕获失败，再接再厉！"
            )

        # 获取嘉宾信息
        guest_result = supabase.table("guests").select("name").eq("id", request.guest_id).execute()
        guest_name = guest_result.data[0]["name"] if guest_result.data else "Unknown"

        # 检查是否已捕获
        existing = supabase.table("captures").select("*").eq("anon_id", request.anon_id).eq("guest_id", request.guest_id).execute()
        if existing.data:
            return CaptureResponse(
                success=True,
                message=f"你之前已经捕获过 {guest_name} 了！",
                guest_name=guest_name
            )

        # 创建捕获记录
        supabase.table("captures").insert({
            "anon_id": request.anon_id,
            "guest_id": request.guest_id,
            "battle_score": request.battle_score
        }).execute()

        # 更新玩家金币和经验
        player_result = supabase.table("anonymous_players").select("*").eq("anon_id", request.anon_id).execute()
        if player_result.data:
            current = player_result.data[0]
            supabase.table("anonymous_players").update({
                "gold": current["gold"] + 50,
                "xp": current["xp"] + 100
            }).eq("anon_id", request.anon_id).execute()

        # 更新排行榜 - 先获取当前值
        leaderboard_result = supabase.table("leaderboard").select("total_captures").eq("anon_id", request.anon_id).execute()
        current_captures = leaderboard_result.data[0]["total_captures"] if leaderboard_result.data else 0

        supabase.table("leaderboard").update({
            "total_captures": current_captures + 1
        }).eq("anon_id", request.anon_id).execute()

        return CaptureResponse(
            success=True,
            message=f"恭喜！你成功捕获了 {guest_name}！",
            guest_name=guest_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


XP_PER_LEVEL = {
    1: 0, 2: 100, 3: 250, 4: 450, 5: 700,
    6: 1000, 7: 1400, 8: 1900, 9: 2500, 10: 3200
}


@router.post("/check-levelup")
def check_level_up(request: LevelUpRequest) -> LevelUpResponse:
    """检查并处理升级"""
    anon_id = request.anon_id
    try:
        supabase = get_supabase()

        # 获取玩家当前数据
        player_result = supabase.table("anonymous_players").select("*").eq("anon_id", anon_id).execute()
        if not player_result.data:
            raise HTTPException(status_code=404, detail="Player not found")

        player = player_result.data[0]
        current_xp = player["xp"]
        current_level = player["level"]

        # 计算升级
        new_level = current_level
        for level, xp_required in XP_PER_LEVEL.items():
            if level > current_level and current_xp >= xp_required:
                new_level = level

        leveled_up = new_level > current_level

        # 初始化属性提升值
        hp_increase = 0
        attack_increase = 0

        if leveled_up:
            # 计算属性提升
            hp_increase = (new_level - current_level) * 10
            attack_increase = (new_level - current_level) * 5

            # 更新玩家属性
            supabase.table("anonymous_players").update({
                "level": new_level,
                "max_hp": player["max_hp"] + hp_increase,
                "hp": player["max_hp"] + hp_increase,  # 回满HP
                "attack": player["attack"] + attack_increase
            }).eq("anon_id", anon_id).execute()

            # 更新排行榜
            supabase.table("leaderboard").update({
                "max_level": new_level
            }).eq("anon_id", anon_id).execute()

        # 获取下一级所需经验
        next_level_xp = XP_PER_LEVEL.get(new_level + 1, XP_PER_LEVEL[10])
        xp_needed = next_level_xp - current_xp

        return LevelUpResponse(
            leveled_up=leveled_up,
            new_level=new_level,
            xp_needed=xp_needed,
            rewards={
                "hp_increase": hp_increase,
                "attack_increase": attack_increase
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SwitchRegionRequest(BaseModel):
    anon_id: str
    region_id: str


@router.get("/regions")
def get_regions(anon_id: str) -> List[dict]:
    """获取玩家可访问的区域"""
    try:
        supabase = get_supabase()

        # 获取玩家等级
        player_result = supabase.table("anonymous_players").select("level").eq("anon_id", anon_id).execute()
        if not player_result.data:
            raise HTTPException(status_code=404, detail="Player not found")

        player_level = player_result.data[0]["level"]

        # 获取所有区域
        regions_result = supabase.table("map_regions").select("*").execute()

        regions = []
        for region in regions_result.data:
            regions.append({
                "id": region["id"],
                "name": region["name"],
                "required_level": region["required_level"],
                "is_unlocked": player_level >= region["required_level"],
                "guest_count": len(region.get("guest_ids", []))
            })

        return regions

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/switch-region")
def switch_region(request: SwitchRegionRequest) -> dict:
    """切换玩家当前区域"""
    anon_id = request.anon_id
    region_id = request.region_id
    try:
        supabase = get_supabase()

        # 验证区域存在且已解锁
        region_result = supabase.table("map_regions").select("*").eq("id", region_id).execute()
        if not region_result.data:
            raise HTTPException(status_code=404, detail="Region not found")

        region = region_result.data[0]

        # 验证玩家等级
        player_result = supabase.table("anonymous_players").select("level").eq("anon_id", anon_id).execute()
        if not player_result.data:
            raise HTTPException(status_code=404, detail="Player not found")

        if player_result.data[0]["level"] < region["required_level"]:
            raise HTTPException(status_code=403, detail="Level not enough")

        # 更新玩家当前区域
        supabase.table("anonymous_players").update({
            "current_region_id": region_id
        }).eq("anon_id", anon_id).execute()

        return {
            "success": True,
            "current_region": region_id,
            "region_name": region["name"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
