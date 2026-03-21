# LennyRPG Phase 2: 探索与收集系统 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成LennyRPG探索与收集系统，包括捕获系统、升级系统、多区域地图解锁、图鉴功能

**Architecture:**
- 前端: Phaser 3 增强地图场景 + React 图鉴页面
- 后端: FastAPI 扩展游戏 API
- 数据库: Supabase 新增表和字段

**Tech Stack:** Phaser 3.80+, React 18, FastAPI, Supabase

---

## 项目结构

```
games/lennyrpg/
├── frontend/
│   └── src/
│       ├── game/
│       │   ├── scenes/
│       │   │   ├── MapScene.ts        # 增强：区域切换、遭遇
│       │   │   ├── BattleScene.ts     # 增强：捕获、升级
│       │   │   └── CollectionScene.ts # 新增：图鉴场景
│       │   └── services/
│       │       └── GameAPI.ts        # 新增：API 客户端
│       └── pages/
│           └── Collection.tsx         # 新增：图鉴页面
├── backend/
│   └── app/
│       ├── api/routes/
│       │   ├── games.py              # 增强：捕获、升级
│       │   └── collection.py          # 新增：图鉴 API
│       └── models/
│           └── schemas.py            # 增强：新增模型
└── supabase/
    └── migrations/
        └── phase2.sql                # 新增：数据库迁移
```

---

## Chunk 1: 捕获系统

### Task 1.1: 增强 BattleScene 捕获功能

**Files:**
- Modify: `games/lennyrpg/frontend/src/game/scenes/BattleScene.ts`

- [ ] **Step 1: 添加捕获状态和UI**

```typescript
// BattleScene.ts 新增属性
interface BattleState {
  // ... 现有属性
  canCapture: boolean
  captureAttempted: boolean
}

// create() 中添加捕获按钮
private createCaptureButton() {
  const btn = this.add.text(400, 450, '捕获', {
    fontSize: '20px',
    backgroundColor: '#4CAF50',
    padding: { x: 20, y: 10 }
  }).setOrigin(0.5)

  btn.setInteractive({ useHandCursor: true })
  btn.on('pointerdown', () => this.attemptCapture())
  btn.setVisible(false)
  return btn
}

private attemptCapture() {
  // 成功率计算
  const baseRate = 0.6
  const rarityBonus = this.getRarityBonus()
  const success = Math.random() < (baseRate + rarityBonus)

  if (success) {
    this.showFeedback('捕获成功!', '#4ade80')
    // TODO: 调用 API 保存捕获
  } else {
    this.showFeedback('捕获失败...', '#ef4444')
  }
}

private getRarityBonus(): number {
  const rarity = this.currentGuest?.rarity
  switch (rarity) {
    case 'common': return 0.2
    case 'rare': return 0.1
    case 'epic': return 0
    case 'legendary': return -0.2
    default: return 0
  }
}
```

- [ ] **Step 2: 战斗胜利后显示捕获选项**

```typescript
private showVictory() {
  // 现有代码...

  // 显示捕获按钮
  this.captureButton.setVisible(true)
  this.captionText.setText('选择: 对战 / 捕获 / 返回')
}
```

- [ ] **Step 3: 测试和提交**

Run: `npm run build`
Expected: 成功构建

- [ ] **Step 4: Commit**

```bash
git add games/lennyrpg/frontend/src/game/scenes/BattleScene.ts
git commit -m "feat(lennyrpg): 添加捕获功能到战斗场景"
```

---

### Task 1.2: 后端捕获 API

**Files:**
- Modify: `games/lennyrpg/backend/app/api/routes/games.py`
- Modify: `games/lennyrpg/backend/app/models/schemas.py`

- [ ] **Step 1: 添加捕获请求模型**

```python
# schemas.py 新增
class CaptureRequest(BaseModel):
    anon_id: str
    guest_id: str
    success: bool
    battle_score: Optional[int] = 0

class CaptureResponse(BaseModel):
    success: bool
    message: str
    guest_name: Optional[str] = None
```

- [ ] **Step 2: 添加捕获 API 端点**

```python
# games.py 新增
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
```

- [ ] **Step 3: 测试和提交**

Run: `cd games/lennyrpg/backend && python -c "from app.main import app; print('OK')"`
Expected: 输出 OK

- [ ] **Step 4: Commit**

```bash
git add games/lennyrpg/backend/app/
git commit -m "feat(lennyrpg): 添加后端捕获API"
```

---

## Chunk 2: 升级系统

### Task 2.1: 升级逻辑后端

**Files:**
- Modify: `games/lennyrpg/backend/app/api/routes/games.py`
- Modify: `games/lennyrpg/backend/app/models/schemas.py`

- [ ] **Step 1: 添加升级相关模型**

```python
# schemas.py 新增
class LevelUpRequest(BaseModel):
    anon_id: str

class LevelUpResponse(BaseModel):
    leveled_up: bool
    new_level: int
    xp_needed: int
    rewards: dict
```

- [ ] **Step 2: 添加升级检查 API**

```python
# games.py 新增
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
                "hp_increase": hp_increase if leveled_up else 0,
                "attack_increase": attack_increase if leveled_up else 0
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 3: 测试和提交**

- [ ] **Step 4: Commit**

```bash
git add games/lennyrpg/backend/app/
git commit -m "feat(lennyrpg): 添加升级系统后端"
```

---

### Task 2.2: 升级 UI 前端

**Files:**
- Modify: `games/lennyrpg/frontend/src/game/scenes/BattleScene.ts`

- [ ] **Step 1: 战斗结束后检查升级**

```typescript
// BattleScene.ts 新增
private async checkLevelUp() {
  try {
    const response = await fetch('/api/games/check-levelup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ anon_id: this.playerId })
    })
    const data = await response.json()

    if (data.leveled_up) {
      this.showLevelUpEffect(data.new_level)
    }
  } catch (e) {
    console.error('升级检查失败', e)
  }
}

private showLevelUpEffect(newLevel: number) {
  const text = this.add.text(400, 300, `升级到 Lv.${newLevel}!`, {
    fontSize: '48px',
    color: '#ffd700',
    stroke: '#000',
    strokeThickness: 4
  }).setOrigin(0.5)

  this.tweens.add({
    targets: text,
    scale: { from: 0.5, to: 1.5 },
    alpha: 0,
    duration: 2000,
    ease: 'Power2'
  })
}
```

- [ ] **Step 2: 在战斗结束后调用**

```typescript
// 修改 showVictory
private showVictory() {
  // 现有代码...
  this.checkLevelUp()
}
```

- [ ] **Step 3: 测试和提交**

- [ ] **Step 4: Commit**

```bash
git add games/lennyrpg/frontend/src/game/scenes/BattleScene.ts
git commit -m "feat(lennyrpg): 添加升级UI效果"
```

---

## Chunk 3: 多区域地图

### Task 3.1: 区域解锁逻辑

**Files:**
- Modify: `games/lennyrpg/backend/app/api/routes/games.py`

- [ ] **Step 1: 添加区域解锁 API**

```python
from pydantic import BaseModel

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
```

- [ ] **Step 2: 添加区域切换 API**

```python
class SwitchRegionRequest(BaseModel):
    anon_id: str
    region_id: str

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
```

- [ ] **Step 3: 测试和提交**

- [ ] **Step 4: Commit**

```bash
git add games/lennyrpg/backend/app/
git commit -m "feat(lennyrpg): 添加区域系统API"
```

---

### Task 3.2: 前端地图区域 UI

**Files:**
- Modify: `games/lennyrpg/frontend/src/game/scenes/MapScene.ts`

- [ ] **Step 1: 加载区域数据**

```typescript
// MapScene.ts 新增
interface Region {
  id: string
  name: string
  required_level: number
  is_unlocked: boolean
  guest_count: number
}

private regions: Region[] = []
private currentRegionIndex = 0

async loadRegions() {
  try {
    const response = await fetch(`/api/games/regions?anon_id=${this.playerId}`)
    this.regions = await response.json()
    this.updateRegionUI()
  } catch (e) {
    console.error('加载区域失败', e)
  }
}
```

- [ ] **Step 2: 添加区域切换按钮**

```typescript
// create() 中添加
private createRegionButtons() {
  const btnLeft = this.add.text(50, 550, '< 区域', {
    fontSize: '16px',
    backgroundColor: '#444',
    padding: { x: 10, y: 5 }
  })
  btnLeft.setInteractive({ useHandCursor: true })
  btnLeft.on('pointerdown', () => this.switchRegion(-1))

  const btnRight = this.add.text(700, 550, '区域 >', {
    fontSize: '16px',
    backgroundColor: '#444',
    padding: { x: 10, y: 5 }
  })
  btnRight.setInteractive({ useHandCursor: true })
  btnRight.on('pointerdown', () => this.switchRegion(1))
}

private async switchRegion(direction: number) {
  const newIndex = this.currentRegionIndex + direction
  if (newIndex < 0 || newIndex >= this.regions.length) return

  const newRegion = this.regions[newIndex]
  if (!newRegion.is_unlocked) {
    this.showFeedback(`需要 Lv.${newRegion.required_level}`, '#ef4444')
    return
  }

  try {
    await fetch('/api/games/switch-region', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        anon_id: this.playerId,
        region_id: newRegion.id
      })
    })
    this.currentRegionIndex = newIndex
    this.loadGuestsForRegion()
  } catch (e) {
    console.error('切换区域失败', e)
  }
}
```

- [ ] **Step 3: 显示区域信息**

```typescript
private updateRegionUI() {
  const region = this.regions[this.currentRegionIndex]
  if (!region) return

  // 更新区域名称显示
  this.regionText.setText(`${region.name} (Lv.${region.required_level})`)

  // 锁定状态
  if (!region.is_unlocked) {
    this.regionText.setColor('#ff0000')
  }
}
```

- [ ] **Step 4: 测试和提交**

- [ ] **Step 5: Commit**

```bash
git add games/lennyrpg/frontend/src/game/scenes/MapScene.ts
git commit -m "feat(lennyrpg): 添加多区域地图功能"
```

---

## Chunk 4: 图鉴功能

### Task 4.1: 图鉴 API

**Files:**
- Create: `games/lennyrpg/backend/app/api/routes/collection.py`
- Modify: `games/lennyrpg/backend/app/main.py`

- [ ] **Step 1: 创建图鉴 API**

```python
# collection.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.supabase_client import get_supabase

router = APIRouter()

@router.get("/summary")
def get_collection_summary(anon_id: str) -> dict:
    """获取图鉴概览"""
    try:
        supabase = get_supabase()

        # 获取所有嘉宾
        all_guests = supabase.table("guests").select("id, rarity, guest_number").execute()

        # 获取已捕获的嘉宾
        captured = supabase.table("captures").select("guest_id").eq("anon_id", anon_id).execute()
        captured_ids = set(c["guest_id"] for c in captured.data)

        # 统计
        summary = {
            "total": len(all_guests.data),
            "captured": len(captured_ids),
            "by_rarity": {
                "common": 0,
                "rare": 0,
                "epic": 0,
                "legendary": 0
            },
            "captured_list": []
        }

        for guest in all_guests.data:
            rarity = guest["rarity"]
            if guest["id"] in captured_ids:
                summary["by_rarity"][rarity] = summary["by_rarity"].get(rarity, 0) + 1
                summary["captured_list"].append(guest["id"])

        return summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guests")
def get_collection_guests(anon_id: str, captured: Optional[bool] = None) -> List[dict]:
    """获取图鉴嘉宾列表"""
    try:
        supabase = get_supabase()

        # 获取所有嘉宾
        guests_result = supabase.table("guests").select("*").order("guest_number").execute()

        # 获取已捕获的嘉宾
        captured_result = supabase.table("captures").select("guest_id, nickname, captured_at").eq("anon_id", anon_id).execute()
        captured_map = {c["guest_id"]: c for c in captured_result.data}

        results = []
        for guest in guests_result.data:
            is_captured = guest["id"] in captured_map

            if captured is not None:
                if captured and not is_captured:
                    continue
                if not captured and is_captured:
                    continue

            guest_data = {
                "id": guest["id"],
                "name": guest["name"],
                "type": guest["type"],
                "rarity": guest["rarity"],
                "guest_number": guest["guest_number"],
                "captured": is_captured
            }

            if is_captured:
                capture_info = captured_map[guest["id"]]
                guest_data["nickname"] = capture_info.get("nickname")
                guest_data["captured_at"] = capture_info.get("captured_at")

            results.append(guest_data)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/guests/{guest_id}/nickname")
def update_nickname(anon_id: str, guest_id: str, nickname: str) -> dict:
    """更新嘉宾昵称"""
    try:
        supabase = get_supabase()

        # 验证已捕获
        captured = supabase.table("captures").select("*").eq("anon_id", anon_id).eq("guest_id", guest_id).execute()
        if not captured.data:
            raise HTTPException(status_code=404, detail="Guest not captured")

        # 更新昵称
        supabase.table("captures").update({
            "nickname": nickname
        }).eq("anon_id", anon_id).eq("guest_id", guest_id).execute()

        return {"success": True, "nickname": nickname}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 2: 注册路由**

```python
# main.py 添加
from app.api.routes import collection
app.include_router(collection.router, prefix="/api/collection", tags=["collection"])
```

- [ ] **Step 3: 测试和提交**

- [ ] **Step 4: Commit**

```bash
git add games/lennyrpg/backend/app/
git commit -m "feat(lennyrpg): 添加图鉴API"
```

---

### Task 4.2: 图鉴页面前端

**Files:**
- Create: `games/lennyrpg/frontend/src/pages/Collection.tsx`
- Modify: `games/lennyrpg/frontend/src/App.tsx`

- [ ] **Step 1: 创建图鉴页面**

```tsx
import { useState, useEffect } from 'react'

interface Guest {
  id: string
  name: string
  type: string
  rarity: string
  guest_number: number
  captured: boolean
  nickname?: string
  captured_at?: string
}

export default function Collection() {
  const [guests, setGuests] = useState<Guest[]>([])
  const [filter, setFilter] = useState<'all' | 'captured' | 'uncaptured'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGuests()
  }, [filter])

  async function loadGuests() {
    setLoading(true)
    try {
      const capturedParam = filter === 'captured' ? 'true' : filter === 'uncaptured' ? 'false' : ''
      const url = `/api/collection/guests?anon_id=${localStorage.getItem('anon_id')}${capturedParam ? '&captured=' + capturedParam : ''}`
      const res = await fetch(url)
      const data = await res.json()
      setGuests(data)
    } catch (e) {
      console.error('加载失败', e)
    }
    setLoading(false)
  }

  const rarityColors: Record<string, string> = {
    common: '#9e9e9e',
    rare: '#2196f3',
    epic: '#9c27b0',
    legendary: '#ffc107'
  }

  return (
    <div style={{ padding: '20px', background: '#1a1a2e', minHeight: '100vh' }}>
      <h1 style={{ color: '#fff' }}>图鉴</h1>

      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => setFilter('all')} style={btnStyle(filter === 'all')}>全部</button>
        <button onClick={() => setFilter('captured')} style={btnStyle(filter === 'captured')}>已捕获</button>
        <button onClick={() => setFilter('uncaptured')} style={btnStyle(filter === 'uncaptured')}>未捕获</button>
      </div>

      {loading ? (
        <p style={{ color: '#fff' }}>加载中...</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '15px' }}>
          {guests.map(guest => (
            <div key={guest.id} style={{
              background: guest.captured ? '#2a2a4a' : '#333',
              border: `2px solid ${rarityColors[guest.rarity]}`,
              borderRadius: '8px',
              padding: '10px',
              opacity: guest.captured ? 1 : 0.5
            }}>
              <div style={{ color: rarityColors[guest.rarity], fontWeight: 'bold' }}>
                {guest.rarity.toUpperCase()}
              </div>
              <div style={{ color: '#fff', fontSize: '18px', margin: '5px 0' }}>
                {guest.captured ? guest.nickname || guest.name : '???'}
              </div>
              <div style={{ color: '#888', fontSize: '12px' }}>
                #{guest.guest_number} · {guest.type}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function btnStyle(active: boolean) {
  return {
    background: active ? '#4CAF50' : '#444',
    color: '#fff',
    border: 'none',
    padding: '8px 16px',
    marginRight: '10px',
    cursor: 'pointer',
    borderRadius: '4px'
  }
}
```

- [ ] **Step 2: 添加路由**

```tsx
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Game from './game'
import Collection from './pages/Collection'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Game />} />
        <Route path="/collection" element={<Collection />} />
      </Routes>
    </BrowserRouter>
  )
}
```

- [ ] **Step 3: 测试和提交**

Run: `cd games/lennyrpg/frontend && npm run build`
Expected: 构建成功

- [ ] **Step 4: Commit**

```bash
git add games/lennyrpg/frontend/src/
git commit -m "feat(lennyrpg): 添加图鉴页面"
```

---

## 验收标准

完成 Phase 2 后，以下功能应可正常工作：

| 功能 | 验收条件 |
|------|----------|
| 捕获系统 | 战斗胜利后可捕获嘉宾，有成功率计算 |
| 升级系统 | 获得足够XP可升级，属性提升 |
| 多区域地图 | 满足等级要求可解锁新区域 |
| 图鉴功能 | 可查看已捕获/未捕获嘉宾，可修改昵称 |

---

## 下一步

Phase 2 完成后，继续 Phase 3:
- [ ] 排行榜
- [ ] 用户系统
- [ ] 智能 NPC 对话
- [ ] AI 问答生成工具
