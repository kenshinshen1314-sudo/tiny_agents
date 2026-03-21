# LennyRPG 产品需求文档 (PRD)

> 基于 https://www.lennysnewsletter.com/p/how-i-built-lennyrpg 复刻
> 版本: 1.0 | 日期: 2026-03-20

---

## 1. 产品概述

### 1.1 产品定义

**LennyRPG** 是一款将 Lenny's Newsletter 播客内容转化为宝可梦风格 RPG 游戏的创新产品。玩家在像素世界中探索，遭遇播客嘉宾，通过产品知识问答与他们对战，胜利后可"捕获"嘉宾并加入收藏。

### 1.2 核心价值

- 将枯燥的播客内容转化为互动游戏体验
- 通过游戏化方式学习产品知识
- 展示 AI 工具（tiny_agents）的开发潜力

### 1.3 目标用户

- Lenny's Newsletter 订阅者
- 产品经理、增长黑客、技术创业者
- AI/游戏开发爱好者

---

## 2. 技术架构

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     前端 (Phaser 3 + React)                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  游戏画布 (Phaser 3)                                 │   │
│  │  - 像素风格 RPG 地图                                 │   │
│  │  - 对战界面                                          │   │
│  │  - 角色/嘉宾 sprites                                │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Web UI (React)                                     │   │
│  │  - 排行榜                                           │   │
│  │  - 图鉴/收藏                                         │   │
│  │  - 设置/个人资料                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (HTTPS)
┌──────────────────────────▼──────────────────────────────────┐
│                    后端 (FastAPI + tiny_agents)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  /api/games/*   游戏核心逻辑                         │   │
│  │  - POST /encounter     遭遇嘉宾                      │   │
│  │  - POST /battle        开始对战                      │   │
│  │  - POST /answer        提交答案                      │   │
│  │  - POST /capture       捕获嘉宾                      │   │
│  │  - GET  /progress      获取进度                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  /api/ai/*      AI 内容生成                          │   │
│  │  - POST /generate/questions  生成问答                │   │
│  │  - POST /generate/avatar    生成头像                │   │
│  │  - POST /generate/dialogue   生成 NPC 对话          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  /api/users/*   用户系统                             │   │
│  │  - POST /register   注册                            │   │
│  │  - POST /login     登录                            │   │
│  │  - GET  /profile   获取资料                         │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  /api/leaderboard/*  排行榜                         │   │
│  │  - GET /rankings    获取排行榜                      │   │
│  │  - POST /submit     提交分数                        │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Supabase (PostgreSQL)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  users   │ │ episodes │ │  guests  │ │ questions    │   │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────────┤   │
│  │ captures │ │map_regions│ │user_items│ │ leaderboard  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端游戏 | Phaser 3.80+ | 2D 像素游戏引擎 |
| 前端框架 | React 18 | UI 界面 |
| 后端框架 | FastAPI | Python 异步 API |
| AI Agent | tiny_agents | 内容生成 |
| 数据库 | Supabase (PostgreSQL) | 数据存储 + Auth |
| 部署前端 | Vercel | 免费 CDN + 部署 |
| 部署后端 | Railway / Render | Python 后端托管 |

### 2.3 AI 集成层次

```
tiny_agents 在游戏中的角色：
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 内容生成 (P1)                                     │
│  - 问答自动生成：读取 transcript，生成 5 道产品问题          │
│  - 头像生成：GPT Image Gen → 像素化 64x64 sprite             │
│  - 背景音乐推荐：从 OpenGameArt 获取                        │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 智能 NPC (P2)                                     │
│  - 战前对话：根据嘉宾背景生成个性化对话                       │
│  - 战后评价：答题表现给予不同反馈                            │
│  - Hint 系统：给玩家提供答题提示（消耗金币）                 │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 动态内容 (P3)                                     │
│  - 每周 Boss：AI 生成特殊挑战                                │
│  - 个性化问答：根据玩家答题历史调整难度                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 功能规格

### 3.1 核心功能列表

| 功能 | 描述 | 优先级 |
|------|------|--------|
| **F1 地图探索** | 像素风格世界，支持区域切换 | P0 |
| **F2 遭遇系统** | 随机遭遇嘉宾，触发对战 | P0 |
| **F3 对战系统** | 问答 RPG，HP/XP 机制 | P0 |
| **F4 捕获系统** | 战胜后捕获嘉宾，图鉴收集 | P0 |
| **F5 升级系统** | XP 积累升级，解锁新区域 | P0 |
| **F6 智能 NPC** | AI 生成对话/评价 | P1 |
| **F7 排行榜** | 全球排名，实时更新 | P1 |
| **F8 问答生成** | tiny_agents 自动生成 | P1 |
| **F9 匿名游玩** | 无需登录保存进度 | P1 |
| **F10 图鉴** | 查看已捕获/未捕获嘉宾 | P2 |

### 3.2 F1: 地图系统

#### 3.2.1 地图设计

- **初始区域**：新手村（Town）
- **区域类型**：
  - `town` - 城镇（恢复 HP，商店）
  - `grass` - 草地（遭遇野生嘉宾）
  - `forest` - 森林（高稀有度嘉宾）
  - `mountain` - 山脉（Boss 区域）
  - `dungeon` - 地下城（传说嘉宾）

#### 3.2.2 区域解锁

| 区域 | 解锁条件 |
|------|----------|
| Grasslands | 初始开放 |
| Forest | 等级 5 |
| Mountain | 等级 10 |
| Dungeon | 等级 20 |

#### 3.2.3 地图交互

- **移动**：方向键 / WASD
- **交互**：E 键与 NPC 对话
- **菜单**：ESC 打开菜单
- **快速旅行**：从城镇传送到已解锁区域

### 3.3 F2: 遭遇系统

#### 3.3.1 遭遇触发

- 玩家在草地/森林/其他区域移动时
- 随机触发遭遇（遇敌率可配置）
- 遭遇时切换到对战界面

#### 3.3.2 嘉宾属性

```python
Guest:
  id: str
  name: str              # 嘉宾姓名
  avatar_url: str         # 像素头像 URL
  type: GuestType        # product | growth | tech | design
  rarity: Rarity          # common | rare | epic | legendary
  hp: int                # 基础 HP (100-500)
  xp_reward: int         # 胜利奖励 XP (50-500)
  bio: str               # AI 生成的简介
  pre_battle_dialog: str # 战前对话
  post_battle_dialog: str # 战后对话
```

### 3.4 F3: 对战系统

#### 3.4.1 对战流程

```
1. 遭遇确认
   ├── 显示嘉宾信息 + 战前对话
   ├── 玩家选择：对战 / 逃跑 / 捕获尝试

2. 问答回合
   ├── 显示问题 + 4 个选项
   ├── 玩家选择答案 (30秒倒计时)
   ├── 正确答案：扣敌方 HP，获得 XP
   ├── 错误答案：扣我方 HP
   └── 重复直到一方 HP ≤ 0

3. 战斗结束
   ├── 玩家胜利：显示战后对话，可捕获
   ├── 玩家失败：传送回城镇，扣金币
   └── 逃跑成功：保留当前进度
```

#### 3.4.2 数值平衡

| 参数 | 数值 |
|------|------|
| 玩家初始 HP | 100 |
| 玩家最大 HP | 100 + (level - 1) * 10 |
| 答对奖励 | 敌方 HP -20 |
| 答错惩罚 | 玩家 HP -15 |
| 题目数量 | 3-5 题（根据难度） |
| 超时惩罚 | 视为答错 |

### 3.5 F4: 捕获系统

#### 3.5.1 捕获规则

- 战斗胜利后可选择捕获
- 捕获成功率 = 基础概率 + 稀有度修正 + 道具修正
- 捕获失败不消耗机会，可无限尝试

#### 3.5.2 成功率公式

```
success_rate = base_rate + rarity_bonus + item_bonus

base_rate = 60%
rarity_bonus:
  - common: +20%
  - rare: +10%
  - epic: 0%
  - legendary: -20%
item_bonus:
  - 捕获卡: +15%
  - 黄金捕获卡: +30%
```

### 3.6 F5: 升级系统

#### 3.6.1 经验值

| 等级 | 所需 XP | 解锁 |
|------|---------|------|
| 1 | 0 | 初始 |
| 2 | 100 | - |
| 3 | 250 | - |
| 4 | 450 | - |
| 5 | 700 | 解锁 Forest 区域 |
| ... | ... | ... |
| 10 | 5000 | 解锁 Mountain 区域 |

#### 3.6.2 升级奖励

- HP 上限 +10
- 攻击力 +5
- 解锁新区域

### 3.7 F6: 智能 NPC (Layer 2)

#### 3.7.1 AI 对话生成

```python
# tiny_agents prompt 模板
PRE_BATTLE_DIALOG_TEMPLATE = """
你是 {guest_name}，{guest_bio}
在 Lenny's Podcast 第 {episode} 期担任嘉宾。

现在有个产品新手玩家想要挑战你。
用 2-3 句话生成你的战前对话，要求：
1. 体现你的专业领域（{guest_type}）
2. 有一定个性但不过于激进
3. 符合产品社区的语言风格

回复只需对话内容，不要其他解释。
"""

POST_BATTLE_DIALOG_TEMPLATE = """
你是 {guest_name}，刚刚输掉了战斗。

根据玩家的表现（答对 {correct}/{total} 题），
用 1-2 句话生成战后评价，要求：
1. 输得口服心服或不服
2. 给出一点建议
3. 保持友好

回复只需对话内容，不要其他解释。
"""
```

#### 3.7.2 Hint 系统

- 每次答题可消耗 10 金币获取提示
- Hint 由 AI 生成，排除 1 个错误选项

### 3.8 F7: 排行榜

#### 3.8.1 排行榜类型

- **全球排行**：总捕获数
- **等级排行**：最高等级
- **连胜排行**：连续战斗胜利次数

#### 3.8.2 数据结构

```sql
leaderboard:
  - user_id: uuid
  - username: string
  - total_captures: int
  - max_level: int
  - win_streak: int
  - updated_at: timestamp
```

### 3.9 F8: 问答自动生成 (tiny_agents)

#### 3.9.1 生成流程

```
1. 导入 transcript
   └── 从 URL / 文件读取

2. AI 分析内容
   └── 提取关键产品概念、增长策略、技术见解

3. 生成问答
   └── 每期生成 5-10 道问题
       ├── question: str
       ├── options: ["A", "B", "C", "D"]
       ├── correct_answer: int
       ├── difficulty: easy/medium/hard
       └── topic: str

4. 人工审核（可选）
   └── 标记需要审核的问题

5. 发布到游戏
   └── 状态变为 published
```

#### 3.9.2 问题难度分布

| 难度 | 比例 | 特征 |
|------|------|------|
| easy | 30% | 基础概念题 |
| medium | 50% | 应用理解题 |
| hard | 20% | 深度分析题 |

### 3.10 F9: 匿名游玩

#### 3.10.1 匿名 ID 生成

- 首次进入游戏自动生成 UUID
- 存储在 localStorage
- 可选绑定账号转移进度

#### 3.10.2 进度迁移机制

```
匿名玩家 → 注册用户 迁移流程：

1. 玩家在设置中选择"绑定账号"
2. 输入邮箱/密码完成注册
3. 系统创建 user 记录
4. 迁移数据：
   ├── level, xp, hp, gold → users 表
   ├── captures → captures 表 (更新 user_id)
   ├── map_progress → map_regions 解锁状态
   └── leaderboard → 更新为正式用户记录
5. 完成后删除 anonymous_players 记录
```

**迁移 API**:
```
POST /api/users/migrate
Body: { "anon_id": "xxx", "email": "xxx", "password": "xxx" }
```

---

### 3.11 F10: 图鉴系统

#### 3.11.1 功能概述

图鉴是玩家已捕获嘉宾的收藏展示界面，类似于宝可梦的图鉴功能。

#### 3.11.2 图鉴结构

```
图鉴主界面
├── 全部嘉宾 (按稀有度分组)
│   ├── Common (已捕获 / 总数)
│   ├── Rare (已捕获 / 总数)
│   ├── Epic (已捕获 / 总数)
│   └── Legendary (已捕获 / 总数)
├── 按类型筛选
│   ├── Product
│   ├── Growth
│   ├── Tech
│   └── Design
└── 已捕获详情
    ├── 嘉宾像素头像
    ├── 昵称 (可自定义)
    ├── 捕获时间
    └── 战斗评分
```

#### 3.11.3 图鉴交互

| 操作 | 触发方式 |
|------|----------|
| 查看详情 | 点击嘉宾卡片 |
| 修改昵称 | 详情页编辑昵称 |
| 筛选 | 顶部 Tab 切换 |
| 排序 | 按捕获时间/稀有度/名称 |

#### 3.11.4 收集奖励

| 收集目标 | 奖励 |
|----------|------|
| 首次捕获 | +50 金币 |
| 收集全部 Common | +200 金币 |
| 收集全部 Rare | +500 金币 + 黄金捕获卡 |
| 收集全部 Epic | +1000 金币 + 传说捕获卡 |
| 收集全部 Legendary | 特殊称号 + 专属头像框 |

#### 3.11.5 API 设计

```
GET  /api/collection           获取图鉴概览
GET  /api/collection/:guest_id 获取嘉宾详情
PUT  /api/collection/:guest_id 更新昵称
GET  /api/collection/rewards   获取收集奖励状态
```

---

### 4. 战斗数值修正 (3.4.2 补充)

#### 战斗伤害公式

为统一攻击力属性的使用，修正战斗伤害计算：

```
答对伤害 = 20 + (attack_power * 0.5)  # 基础20 + 攻击力加成
答错伤害 = 15 + (enemy_attack * 0.3)   # 基础15 + 敌方攻击力
```

**攻击力来源**：
- 初始攻击力: 10
- 每级提升: +5
- 装备加成: 后续版本添加

---

### 3.12 商店系统

#### 3.12.1 商店位置

- 城镇区域设有商店 NPC
- 按 `S` 键或点击商店图标打开

#### 3.12.2 出售商品

| 商品 | 价格 | 效果 |
|------|------|------|
| HP 药水 (小) | 30 金币 | 恢复 30 HP |
| HP 药水 (中) | 80 金币 | 恢复 80 HP |
| HP 药水 (大) | 150 金币 | 恢复全部 HP |
| 捕获卡 | 50 金币 | 捕获成功率 +15% |
| 黄金捕获卡 | 120 金币 | 捕获成功率 +30% |
| 定时器延长 | 40 金币 | 本次对战 +15 秒 |

#### 3.12.3 金币获取

| 来源 | 数量 |
|------|------|
| 战胜嘉宾 | 20-50 (根据稀有度) |
| 首次捕获 | +50 |
| 每日登录 | +10 |
| 收集奖励 | 见 3.11.4 |

#### 3.12.4 API 设计

```
GET  /api/shop/items          获取商品列表
POST /api/shop/buy           购买商品
GET  /api/shop/inventory     获取背包
```

---

### 3.13 数据获取 (补充)

#### 3.13.1 Lenny 播客数据获取

初始 10 期数据采用手动导入方式：

1. 从 Lenny's Newsletter GitHub 获取 transcript
2. 解析 JSON/TXT 文件
3. 批量导入到 `episodes` 表

**数据源**:
- GitHub: `https://github.com/lennysan/lennys-podcast` (如有)
- 或手动整理 10 期 transcript 文件

#### 3.13.2 扩展支持

后续扩展时，可添加自动抓取：
- RSS 订阅解析
- 定时任务拉取新期数
- 触发 AI 自动生成

---

## 4. 数据模型

### 4.1 数据库 Schema

```sql
-- 4.1.1 用户表
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(50) UNIQUE,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  level INTEGER DEFAULT 1,
  xp INTEGER DEFAULT 0,
  hp INTEGER DEFAULT 100,
  gold INTEGER DEFAULT 100,
  current_region_id VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 4.1.2 匿名玩家表
CREATE TABLE anonymous_players (
  anon_id VARCHAR(64) PRIMARY KEY,
  level INTEGER DEFAULT 1,
  xp INTEGER DEFAULT 0,
  hp INTEGER DEFAULT 100,
  gold INTEGER DEFAULT 100,
  current_region_id VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 4.1.3 播客期数表
CREATE TABLE episodes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  number INTEGER UNIQUE,
  title VARCHAR(255),
  transcript_url TEXT,
  status VARCHAR(20) DEFAULT 'pending', -- pending, generating, published
  guest_id UUID REFERENCES guests(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- 4.1.4 嘉宾表
CREATE TABLE guests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100),
  avatar_url TEXT,
  type VARCHAR(20), -- product, growth, tech, design
  rarity VARCHAR(20), -- common, rare, epic, legendary
  bio TEXT,
  pre_battle_dialog TEXT,
  post_battle_dialog TEXT,
  hp INTEGER DEFAULT 100,
  xp_reward INTEGER DEFAULT 50,
  episode_id UUID REFERENCES episodes(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- 4.1.5 问答表
CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  guest_id UUID REFERENCES guests(id),
  question TEXT,
  options JSONB, -- ["A. xxx", "B. xxx", "C. xxx", "D. xxx"]
  correct_answer INTEGER,
  difficulty VARCHAR(20), -- easy, medium, hard
  topic VARCHAR(100),
  used_count INTEGER DEFAULT 0,
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, published
  created_at TIMESTAMP DEFAULT NOW()
);

-- 4.1.6 捕获记录表
CREATE TABLE captures (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  anon_id VARCHAR(64) REFERENCES anonymous_players(anon_id),
  guest_id UUID REFERENCES guests(id),
  battle_score INTEGER,
  nickname VARCHAR(50),
  captured_at TIMESTAMP DEFAULT NOW()
);

-- 4.1.7 地图区域表
CREATE TABLE map_regions (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  required_level INTEGER DEFAULT 1,
  is_unlocked BOOLEAN DEFAULT FALSE,
  guest_ids JSONB, -- 该区域嘉宾 ID 列表
  background_url TEXT
);

-- 4.1.8 排行榜表
CREATE TABLE leaderboard (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  anon_id VARCHAR(64) REFERENCES anonymous_players(anon_id),
  total_captures INTEGER DEFAULT 0,
  max_level INTEGER DEFAULT 1,
  win_streak INTEGER DEFAULT 0,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4.2 扩展性设计

#### 4.2.1 数据驱动扩展

- **新增播客**：只需在 `episodes` 表添加记录
- **自动生成**：调用 `/api/ai/generate/questions` 自动生成内容

#### 4.2.2 配置化扩展

```python
# 配置示例 (config/game_config.py)
GUEST_TYPES = ["product", "growth", "tech", "design"]
RARITY_OPTIONS = ["common", "rare", "epic", "legendary"]
DIFFICULTY_LEVELS = ["easy", "medium", "hard", "epic"]

REGION_CONFIG = {
    "grasslands": {
        "required_level": 1,
        "guest_types": ["product", "growth"],
        "rarity_weights": {"common": 0.7, "rare": 0.3}
    },
    "forest": {
        "required_level": 5,
        "guest_types": ["tech", "design", "growth"],
        "rarity_weights": {"common": 0.3, "rare": 0.5, "epic": 0.2}
    }
}
```

---

## 5. 验收标准

### 5.1 功能验收

| 功能 | 验收条件 |
|------|----------|
| 地图探索 | 玩家可在像素地图中移动，可进入不同区域 |
| 遭遇系统 | 移动时随机触发遭遇，显示嘉宾信息 |
| 对战系统 | 问答正确扣敌方 HP，错误扣己方 HP，有倒计时 |
| 捕获系统 | 胜利后可捕获，有成功率计算 |
| 升级系统 | XP 积累可升级，解锁区域 |
| 排行榜 | 显示 Top 100 玩家排名 |
| 问答生成 | 导入 transcript 可自动生成 5 道问题 |
| 匿名游玩 | 无需登录可保存进度到 localStorage |

### 5.2 性能要求

| 指标 | 要求 |
|------|------|
| 首屏加载 | < 3 秒 |
| 对战响应 | < 500ms |
| API 响应 | < 200ms |
| 帧率 | 30+ FPS |

### 5.3 初始数据 (10 期)

| 期数 | 嘉宾 | 类型 | 稀有度 |
|------|------|------|--------|
| 1 | Default Guest 1 | product | common |
| 2 | Default Guest 2 | growth | common |
| 3 | Default Guest 3 | tech | rare |
| 4 | Default Guest 4 | design | rare |
| 5 | Default Guest 5 | product | epic |
| 6-10 | ... | ... | ... |

---

## 6. 开发计划

### 6.1 Phase 1: 核心对战 (Week 1-2)

- [ ] 项目初始化 (Phaser 3 + FastAPI)
- [ ] Supabase 数据库搭建
- [ ] 地图系统原型
- [ ] 遭遇 + 对战系统
- [ ] 基础问答数据 (10 期)

### 6.2 Phase 2: 探索与收集 (Week 3-4)

- [ ] 捕获系统
- [ ] 升级系统
- [ ] 多区域地图
- [ ] 图鉴功能

### 6.3 Phase 3: 社交与 AI (Week 5-6)

- [ ] 排行榜
- [ ] 用户系统
- [ ] 智能 NPC 对话
- [ ] AI 问答生成工具

### 6.4 Phase 4: 优化与发布 (Week 7-8)

- [ ] 性能优化
- [ ] UI/UX 打磨
- [ ] 测试与 Bug 修复
- [ ] 部署上线

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 播客数据版权 | 高 | 使用公开数据+Lenny授权 |
| AI 生成质量问题 | 中 | 人工审核流程 |
| Supabase 成本 | 低 | 免费配额足够初期使用 |
| Phaser 开发复杂度 | 中 | 复用开源素材 |

---

## 8. 附录

### 8.1 参考资源

- 原版 LennyRPG: https://www.lennysnewsletter.com/p/how-i-built-lennyrpg
- Phaser 3: https://phaser.io/
- tiny_agents: 项目内 `tiny_agents/` 目录

### 8.2 像素素材来源

- OpenGameArt.org (免费)
- Itch.io (CC0 素材)
- GPT Image Gen → 像素化处理

### 8.3 API 端点汇总

```
POST /api/games/encounter    遭遇嘉宾
POST /api/games/battle       开始对战
POST /api/games/answer       提交答案
POST /api/games/capture      捕获嘉宾
GET  /api/games/progress     获取进度

POST /api/ai/generate/questions  生成问答
POST /api/ai/generate/avatar     生成头像
POST /api/ai/generate/dialogue   生成对话

POST /api/users/register   注册
POST /api/users/login      登录
GET  /api/users/profile    获取资料

GET  /api/leaderboard/rankings   获取排行榜
POST /api/leaderboard/submit    提交分数
```
