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
