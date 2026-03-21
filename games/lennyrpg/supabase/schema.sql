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