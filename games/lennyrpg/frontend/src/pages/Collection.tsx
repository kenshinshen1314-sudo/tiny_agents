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
  const [summary, setSummary] = useState<any>(null)

  const anonId = localStorage.getItem('anon_id') || 'test-player'

  useEffect(() => {
    loadData()
  }, [filter])

  async function loadData() {
    setLoading(true)
    try {
      // 加载概览
      const summaryRes = await fetch(`/api/collection/summary?anon_id=${anonId}`)
      setSummary(await summaryRes.json())

      // 加载嘉宾列表
      const capturedParam = filter === 'captured' ? 'true' : filter === 'uncaptured' ? 'false' : ''
      const url = `/api/collection/guests?anon_id=${anonId}${capturedParam ? '&captured=' + capturedParam : ''}`
      const res = await fetch(url)
      setGuests(await res.json())
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
      <h1 style={{ color: '#fff', marginBottom: '20px' }}>图鉴</h1>

      {summary && (
        <div style={{ marginBottom: '20px', padding: '15px', background: '#2a2a4a', borderRadius: '8px' }}>
          <div style={{ color: '#fff', fontSize: '18px' }}>
            已捕获: {summary.captured} / {summary.total}
          </div>
          <div style={{ display: 'flex', gap: '15px', marginTop: '10px' }}>
            {Object.entries(summary.by_rarity).map(([rarity, count]: [string, any]) => (
              <div key={rarity} style={{ color: rarityColors[rarity] }}>
                {rarity}: {count}
              </div>
            ))}
          </div>
        </div>
      )}

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
              <div style={{ color: rarityColors[guest.rarity], fontWeight: 'bold', fontSize: '12px' }}>
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

      <a href="/" style={{ display: 'inline-block', marginTop: '20px', color: '#88ccff' }}>
        ← 返回游戏
      </a>
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
