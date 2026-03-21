# LennyRPG Phase 1: 核心对战系统 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成LennyRPG核心对战系统，包括项目初始化、Supabase数据库搭建、地图系统、遭遇与对战系统

**Architecture:**
- 前端: Phaser 3 (游戏) + React (UI)
- 后端: FastAPI + tiny_agents
- 数据库: Supabase (PostgreSQL)

**Tech Stack:** Phaser 3.80+, React 18, FastAPI, Supabase, tiny_agents

---

## 项目结构

```
games/lennyrpg/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── game/               # Phaser 3 游戏
│   │   │   ├── scenes/         # 游戏场景
│   │   │   │   ├── BootScene.ts
│   │   │   │   ├── MapScene.ts  # 地图探索
│   │   │   │   └── BattleScene.ts # 对战系统
│   │   │   ├── sprites/         # 精灵图
│   │   │   ├── assets/          # 资源文件
│   │   │   └── index.ts         # 游戏入口
│   │   ├── ui/                  # React UI
│   │   │   ├── components/
│   │   │   └── pages/
│   │   ├── api/                 # API 客户端
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── backend/                     # 后端项目
│   ├── app/
│   │   ├── api/                 # API 路由
│   │   │   └── routes/
│   │   │       ├── games.py
│   │   │       └── ai.py
│   │   ├── models/             # 数据模型
│   │   ├── services/           # 业务逻辑
│   │   │   └── tiny_agents/    # AI 生成
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
└── supabase/
    └── migrations/              # 数据库迁移
```

---

## Chunk 1: 项目初始化与数据库

### Task 1.1: 创建前端项目

**Files:**
- Create: `games/lennyrpg/frontend/package.json`
- Create: `games/lennyrpg/frontend/vite.config.ts`
- Create: `games/lennyrpg/frontend/tsconfig.json`
- Create: `games/lennyrpg/frontend/index.html`
- Create: `games/lennyrpg/frontend/src/main.tsx`
- Create: `games/lennyrpg/frontend/src/App.tsx`

- [ ] **Step 1: Write package.json**

```json
{
  "name": "lennyrpg-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "phaser": "^3.80.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 2: Write vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **Step 3: Write tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

- [ ] **Step 4: Write index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>LennyRPG</title>
    <style>
      body { margin: 0; background: #1a1a2e; }
      #root { width: 100vw; height: 100vh; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 5: Write main.tsx**

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 6: Write App.tsx**

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Game from './game'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Game />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

- [ ] **Step 7: Commit**

```bash
cd games/lennyrpg/frontend && npm install
git add games/lennyrpg/frontend/
git commit -m "feat(lennyrpg): 初始化前端项目"
```

### Task 1.2: 创建后端项目

**Files:**
- Create: `games/lennyrpg/backend/requirements.txt`
- Create: `games/lennyrpg/backend/.env.example`
- Create: `games/lennyrpg/backend/app/__init__.py`
- Create: `games/lennyrpg/backend/app/main.py`
- Create: `games/lennyrpg/backend/app/config.py`

- [ ] **Step 1: Write requirements.txt**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
supabase==2.3.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.26.0
```

- [ ] **Step 2: Write .env.example**

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_key
```

- [ ] **Step 3: Write config.py**

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 4: Write main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import games, ai

app = FastAPI(title="LennyRPG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Commit**

```bash
cd games/lennyrpg/backend && pip install -r requirements.txt
git add games/lennyrpg/backend/
git commit -m "feat(lennyrpg): 初始化后端项目"
```

---

## Chunk 2: Supabase 数据库

### Task 2.1: 创建数据库 Schema

**Files:**
- Create: `games/lennyrpg/supabase/schema.sql`

- [ ] **Step 1: Write schema.sql**

```sql
-- LennyRPG Database Schema

-- 匿名玩家表 (无需登录游玩)
CREATE TABLE anonymous_players (
    anon_id VARCHAR(64) PRIMARY KEY,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    hp INTEGER DEFAULT 100,
    max_hp INTEGER DEFAULT 100,
    attack INTEGER DEFAULT 10,
    gold INTEGER DEFAULT 100,
    current_region_id VARCHAR(50) DEFAULT 'grasslands',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 嘉宾表
CREATE TABLE guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    type VARCHAR(20) NOT NULL, -- product, growth, tech, design
    rarity VARCHAR(20) NOT NULL, -- common, rare, epic, legendary
    bio TEXT,
    pre_battle_dialog TEXT,
    post_battle_dialog TEXT,
    hp INTEGER DEFAULT 100,
    attack INTEGER DEFAULT 10,
    xp_reward INTEGER DEFAULT 50,
    guest_number INTEGER NOT NULL, -- 播客期号
    created_at TIMESTAMP DEFAULT NOW()
);

-- 问答表
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id UUID NOT NULL REFERENCES guests(id),
    question TEXT NOT NULL,
    options JSONB NOT NULL, -- ["A. xxx", "B. xxx", "C. xxx", "D. xxx"]
    correct_answer INTEGER NOT NULL, -- 0-3
    difficulty VARCHAR(20) DEFAULT 'medium', -- easy, medium, hard
    topic VARCHAR(100),
    used_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, published
    created_at TIMESTAMP DEFAULT NOW()
);

-- 捕获记录表
CREATE TABLE captures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anon_id VARCHAR(64) NOT NULL REFERENCES anonymous_players(anon_id),
    guest_id UUID NOT NULL REFERENCES guests(id),
    battle_score INTEGER,
    nickname VARCHAR(50),
    captured_at TIMESTAMP DEFAULT NOW()
);

-- 地图区域表
CREATE TABLE map_regions (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    required_level INTEGER DEFAULT 1,
    is_unlocked BOOLEAN DEFAULT FALSE,
    guest_ids JSONB, -- 该区域嘉宾 ID 列表
    background_url TEXT
);

-- 排行榜表
CREATE TABLE leaderboard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anon_id VARCHAR(64) NOT NULL REFERENCES anonymous_players(anon_id),
    username VARCHAR(50),
    total_captures INTEGER DEFAULT 0,
    max_level INTEGER DEFAULT 1,
    win_streak INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 初始化地图区域
INSERT INTO map_regions (id, name, required_level, is_unlocked, guest_ids) VALUES
('town', 'Town', 1, true, '[]'),
('grasslands', 'Grasslands', 1, true, '[]'),
('forest', 'Forest', 5, false, '[]'),
('mountain', 'Mountain', 10, false, '[]'),
('dungeon', 'Dungeon', 20, false, '[]');
```

- [ ] **Step 2: Commit**

```bash
git add games/lennyrpg/supabase/
git commit -m "feat(lennyrpg): 添加数据库 schema"
```

---

## Chunk 3: 地图系统 (Phaser 3)

### Task 3.1: 创建 Phaser 游戏入口

**Files:**
- Create: `games/lennyrpg/frontend/src/game/index.ts`
- Create: `games/lennyrpg/frontend/src/game/scenes/BootScene.ts`
- Create: `games/lennyrpg/frontend/src/game/scenes/MapScene.ts`
- Create: `games/lennyrpg/frontend/src/game/scenes/BattleScene.ts`

- [ ] **Step 1: Write game/index.ts**

```typescript
import Phaser from 'phaser'
import MapScene from './scenes/MapScene'
import BattleScene from './scenes/BattleScene'

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: 'game-container',
  backgroundColor: '#1a1a2e',
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: 0 },
      debug: false
    }
  },
  scene: [MapScene, BattleScene]
}

export function startGame() {
  const game = new Phaser.Game(config)
  return game
}
```

- [ ] **Step 2: Write BootScene.ts**

```typescript
import Phaser from 'phaser'

export default class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' })
  }

  preload() {
    // 加载资源
    this.load.image('player', '/assets/sprites/player.png')
    this.load.image('grass', '/assets/tiles/grass.png')
    this.load.image('tree', '/assets/tiles/tree.png')
    this.load.image('guest', '/assets/sprites/guest.png')
  }

  create() {
    this.scene.start('MapScene')
  }
}
```

- [ ] **Step 3: Write MapScene.ts**

```typescript
import Phaser from 'phaser'

export default class MapScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private playerSpeed = 160

  constructor() {
    super({ key: 'MapScene' })
  }

  create() {
    // 创建测试地图 (使用色块代替)
    const graphics = this.add.graphics()

    // 草地背景
    graphics.fillStyle(0x4a7c59)
    graphics.fillRect(0, 0, 800, 600)

    // 城镇区域 (左上方)
    graphics.fillStyle(0x8b7355)
    graphics.fillRect(50, 50, 150, 100)
    this.add.text(80, 90, 'Town', { fontSize: '16px', color: '#fff' })

    // 森林区域 (右上方)
    graphics.fillStyle(0x2d5a27)
    graphics.fillRect(500, 50, 200, 150)
    this.add.text(560, 110, 'Forest\n(Lv.5)', { fontSize: '14px', color: '#fff', align: 'center' })

    // 山脉区域 (下方)
    graphics.fillStyle(0x696969)
    graphics.fillRect(300, 400, 250, 150)
    this.add.text(375, 460, 'Mountain\n(Lv.10)', { fontSize: '14px', color: '#fff', align: 'center' })

    // 创建玩家
    this.player = this.physics.add.sprite(125, 125, 'player')
    this.player.setCollideWorldBounds(true)

    // 键盘输入
    this.cursors = this.input.keyboard.createCursorKeys()

    // UI: 显示玩家状态
    this.showPlayerUI()
  }

  update() {
    const { left, right, up, down } = this.cursors

    this.player.setVelocity(0)

    if (left.isDown) this.player.setVelocityX(-this.playerSpeed)
    else if (right.isDown) this.player.setVelocityX(this.playerSpeed)

    if (up.isDown) this.player.setVelocityY(-this.playerSpeed)
    else if (down.isDown) this.player.setVelocityY(this.playerSpeed)
  }

  private showPlayerUI() {
    const uiContainer = this.add.container(10, 10)

    const bg = this.add.graphics()
    bg.fillStyle(0x000000, 0.7)
    bg.fillRect(0, 0, 150, 80)

    const levelText = this.add.text(10, 10, 'Lv.1', { fontSize: '14px', color: '#ffd700' })
    const hpText = this.add.text(10, 30, 'HP: 100/100', { fontSize: '14px', color: '#ff6b6b' })
    const goldText = this.add.text(10, 50, 'Gold: 100', { fontSize: '14px', color: '#ffd700' })

    uiContainer.add([bg, levelText, hpText, goldText])
  }
}
```

- [ ] **Step 4: Write BattleScene.ts**

```typescript
import Phaser from 'phaser'

interface Question {
  id: string
  question: string
  options: string[]
  correct_answer: number
}

export default class BattleScene extends Phaser.Scene {
  private currentQuestion!: Question
  private playerHP = 100
  private playerMaxHP = 100
  private enemyHP = 100
  private enemyMaxHP = 100
  private attackPower = 10

  constructor() {
    super({ key: 'BattleScene' })
  }

  init(data: { guestId: string; questions: Question[] }) {
    this.currentQuestion = data.questions[0]
    this.enemyMaxHP = 100 // TODO: 从guest获取
    this.enemyHP = this.enemyMaxHP
  }

  create() {
    // 战斗背景
    const bg = this.add.graphics()
    bg.fillStyle(0x2a2a4a)
    bg.fillRect(0, 0, 800, 600)

    // 敌方信息
    this.add.text(500, 50, 'Guest', { fontSize: '20px', color: '#fff' })
    this.add.text(500, 80, `HP: ${this.enemyHP}/${this.enemyMaxHP}`, { fontSize: '16px', color: '#ff6b6b' })

    // 玩家信息
    this.add.text(50, 350, 'Player', { fontSize: '20px', color: '#fff' })
    this.add.text(50, 380, `HP: ${this.playerHP}/${this.playerMaxHP}`, { fontSize: '16px', color: '#ff6b6b' })

    // 问题显示
    this.add.text(100, 200, this.currentQuestion.question, {
      fontSize: '18px',
      color: '#fff',
      wordWrap: { width: 600 }
    })

    // 选项按钮
    this.createOptionButtons()

    // 返回按钮
    const backBtn = this.add.text(50, 550, '< Back to Map', { fontSize: '16px', color: '#88ccff' })
    backBtn.setInteractive({ useHandCursor: true })
    backBtn.on('pointerdown', () => {
      this.scene.start('MapScene')
    })
  }

  private createOptionButtons() {
    const yStart = 280
    const options = this.currentQuestion.options

    options.forEach((option, index) => {
      const btn = this.add.text(120, yStart + index * 50, option, {
        fontSize: '16px',
        color: '#fff',
        backgroundColor: '#444',
        padding: { x: 10, y: 5 }
      })

      btn.setInteractive({ useHandCursor: true })

      btn.on('pointerdown', () => {
        this.handleAnswer(index)
      })
    })
  }

  private handleAnswer(answerIndex: number) {
    const isCorrect = answerIndex === this.currentQuestion.correct_answer

    if (isCorrect) {
      // 答对: 扣敌方HP
      const damage = Math.floor(20 + this.attackPower * 0.5)
      this.enemyHP = Math.max(0, this.enemyHP - damage)

      this.showFeedback('Correct!', '#4ade80')

      if (this.enemyHP <= 0) {
        this.showVictory()
      }
    } else {
      // 答错: 扣玩家HP
      this.playerHP = Math.max(0, this.playerHP - 15)
      this.showFeedback('Wrong!', '#ef4444')

      if (this.playerHP <= 0) {
        this.showDefeat()
      }
    }

    // 更新UI
    this.scene.restart()
  }

  private showFeedback(text: string, color: string) {
    const feedback = this.add.text(400, 300, text, {
      fontSize: '32px',
      color: color
    }).setOrigin(0.5)

    this.tweens.add({
      targets: feedback,
      alpha: 0,
      duration: 1000
    })
  }

  private showVictory() {
    const msg = this.add.text(400, 300, 'VICTORY!', {
      fontSize: '48px',
      color: '#ffd700'
    }).setOrigin(0.5)

    setTimeout(() => {
      this.scene.start('MapScene')
    }, 2000)
  }

  private showDefeat() {
    const msg = this.add.text(400, 300, 'DEFEATED...', {
      fontSize: '48px',
      color: '#ef4444'
    }).setOrigin(0.5)

    setTimeout(() => {
      this.playerHP = this.playerMaxHP
      this.scene.start('MapScene')
    }, 2000)
  }
}
```

- [ ] **Step 5: Update App.tsx to mount game**

```typescript
import { useEffect, useRef } from 'react'
import { startGame } from './game'

function Game() {
  const gameRef = useRef<any>(null)

  useEffect(() => {
    gameRef.current = startGame()
    return () => {
      gameRef.current?.destroy(true)
    }
  }, [])

  return <div id="game-container" />
}

export default Game
```

- [ ] **Step 6: Commit**

```bash
git add games/lennyrpg/frontend/src/game/
git commit -m "feat(lennyrpg): 添加Phaser地图和对战场景"
```

---

## Chunk 4: 后端 API

### Task 4.1: 游戏 API 路由

**Files:**
- Create: `games/lennyrpg/backend/app/api/__init__.py`
- Create: `games/lennyrpg/backend/app/api/routes/__init__.py`
- Create: `games/lennyrpg/backend/app/api/routes/games.py`
- Create: `games/lennyrpg/backend/app/api/routes/ai.py`
- Create: `games/lennyrpg/backend/app/models/__init__.py`
- Create: `games/lennyrpg/backend/app/models/schemas.py`

- [ ] **Step 1: Write schemas.py**

```python
from pydantic import BaseModel
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
    answer: int

class BattleResponse(BaseModel):
    correct: bool
    player_damage: int
    enemy_damage: int
    player_hp: int
    enemy_hp: int
    battle_over: bool
    victory: Optional[bool]
```

- [ ] **Step 2: Write games.py**

```python
from fastapi import APIRouter, HTTPException
from app.models.schemas import Player, Guest, Question, BattleRequest, BattleResponse
from app.supabase_client import get_supabase
import random
import uuid

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

class CaptureRequest(BaseModel):
    anon_id: str
    guest_id: str
    success: bool

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
        "gold": 50  # 捕获奖励
    }).eq("anon_id", anon_id).execute()

    # 更新排行榜
    supabase.table("leaderboard").update({
        "total_captures": 1
    }).eq("anon_id", anon_id).execute()

    return {"success": True, "message": f"Guest captured!"}
```

- [ ] **Step 3: Write supabase_client.py**

```python
from supabase import create_client
from app.config import settings

def get_supabase():
    return create_client(settings.supabase_url, settings.supabase_key)
```

- [ ] **Step 4: Write ai.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.supabase_client import get_supabase

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
            question="How does {request.guest_name} approach hiring?",
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
```

- [ ] **Step 5: Commit**

```bash
git add games/lennyrpg/backend/app/
git commit -m "feat(lennyrpg): 添加后端API路由"
```

---

## Chunk 5: 初始数据

### Task 5.1: 种子数据

**Files:**
- Create: `games/lennyrpg/supabase/seed.sql`

- [ ] **Step 1: Write seed.sql**

```sql
-- 插入10位示例嘉宾

INSERT INTO guests (id, name, type, rarity, bio, hp, attack, xp_reward, guest_number) VALUES
-- Common (1-4)
(gen_random_uuid(), 'Sarah Chen', 'product', 'common', 'Product leader at Stripe', 80, 8, 40, 1),
(gen_random_uuid(), 'Mike Davidson', 'growth', 'common', 'Growth at Notion', 80, 8, 40, 2),
(gen_random_uuid(), 'Emma Wilson', 'tech', 'common', 'CTO at Figma', 90, 10, 50, 3),
(gen_random_uuid(), 'Alex Park', 'design', 'common', 'Design director at Airbnb', 80, 8, 40, 4),
-- Rare (5-7)
(gen_random_uuid(), 'Jordan Lee', 'product', 'rare', 'Former VP Product at Google', 100, 12, 70, 5),
(gen_random_uuid(), 'Sam Taylor', 'growth', 'rare', 'Growth lead at Uber', 100, 12, 70, 6),
(gen_random_uuid(), 'Chris Wong', 'tech', 'rare', 'Engineering manager at Meta', 110, 14, 80, 7),
-- Epic (8-9)
(gen_random_uuid(), 'Riley Morgan', 'product', 'epic', 'Founder of successful SaaS', 120, 16, 100, 8),
(gen_random_uuid(), 'Casey Rivera', 'growth', 'epic', 'Best-selling author on growth', 120, 16, 100, 9),
-- Legendary (10)
(gen_random_uuid(), 'Taylor Swift', 'tech', 'legendary', 'Legendary engineer turned investor', 150, 20, 150, 10);

-- 更新地图区域的guest_ids
UPDATE map_regions SET guest_ids = (
    SELECT json_agg(id) FROM guests WHERE guest_number <= 4
) WHERE id = 'grasslands';

UPDATE map_regions SET guest_ids = (
    SELECT json_agg(id) FROM guests WHERE guest_number BETWEEN 5 AND 7
) WHERE id = 'forest';

UPDATE map_regions SET guest_ids = (
    SELECT json_agg(id) FROM guests WHERE guest_number BETWEEN 8 AND 9
) WHERE id = 'mountain';

UPDATE map_regions SET guest_ids = (
    SELECT json_agg(id) FROM guests WHERE guest_number = 10
) WHERE id = 'dungeon';

-- 插入示例问答
INSERT INTO questions (guest_id, question, options, correct_answer, difficulty, topic, status)
SELECT
    id,
    'Sample question for ' || name,
    '["A. Option A", "B. Option B", "C. Option C", "D. Option D"]'::jsonb,
    0,
    'easy',
    type,
    'published'
FROM guests
WHERE guest_number <= 5;
```

- [ ] **Step 2: Commit**

```bash
git add games/lennyrpg/supabase/
git commit -m "feat(lennyrpg): 添加种子数据"
```

---

## 验收标准

完成 Phase 1 后，以下功能应可正常工作：

| 功能 | 验收条件 |
|------|----------|
| 前端运行 | `npm run dev` 启动成功，显示游戏画布 |
| 后端运行 | `uvicorn app.main:app` 启动成功，/api/health 返回 ok |
| 地图移动 | 玩家可使用方向键在地图上移动 |
| 遭遇触发 | 移动时可触发遭遇（当前为模拟） |
| 对战答题 | 显示问题，可选择答案，有正确/错误反馈 |
| HP 扣除 | 正确答案扣敌方HP，错误答案扣己方HP |
| 胜利/失败 | HP归零时显示胜利/失败画面 |
| 玩家注册 | POST /api/games/register 创建玩家 |
| 数据持久化 | Supabase 数据库正确存储玩家数据 |

---

## 下一步

Phase 1 完成后，继续 Phase 2:
- [ ] 捕获系统（真正实现）
- [ ] 升级系统（XP/等级）
- [ ] 多区域地图（解锁逻辑）
- [ ] 图鉴功能
