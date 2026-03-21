import Phaser from 'phaser'

interface Region {
  id: string
  name: string
  required_level: number
  is_unlocked: boolean
  guest_count: number
}

export default class MapScene extends Phaser.Scene {
  private player!: Phaser.GameObjects.Rectangle
  private playerBody!: Phaser.Physics.Arcade.Body
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private playerSpeed = 160
  private regions: Region[] = []
  private currentRegionIndex = 0
  private regionText!: Phaser.GameObjects.Text
  private feedbackText!: Phaser.GameObjects.Text

  constructor() {
    super({ key: 'MapScene' })
  }

  async loadRegions() {
    try {
      const response = await fetch(`/api/games/regions?anon_id=${(this as any).playerId || 'test-player'}`)
      this.regions = await response.json()
      this.updateRegionUI()
    } catch (e) {
      console.error('加载区域失败', e)
    }
  }

  async switchRegion(direction: number) {
    const newIndex = this.currentRegionIndex + direction
    if (newIndex < 0 || newIndex >= this.regions.length) return

    const newRegion = this.regions[newIndex]
    if (!newRegion.is_unlocked) {
      this.showFeedback(`需要 Lv.${newRegion.required_level}`, '#ef4444')
      return
    }

    try {
      const response = await fetch('/api/games/switch-region', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          anon_id: (this as any).playerId || 'test-player',
          region_id: newRegion.id
        })
      })
      const data = await response.json()
      if (data.success) {
        this.currentRegionIndex = newIndex
        this.showFeedback(`已切换到 ${data.region_name}`, '#4ade80')
        this.loadGuestsForRegion()
      }
    } catch (e) {
      console.error('切换区域失败', e)
    }
  }

  private loadGuestsForRegion() {
    // 刷新当前区域的访客信息
    if (this.regions[this.currentRegionIndex]) {
      this.updateRegionUI()
    }
  }

  private updateRegionUI() {
    if (this.regionText && this.regions[this.currentRegionIndex]) {
      const region = this.regions[this.currentRegionIndex]
      this.regionText.setText(`${region.name} (在线: ${region.guest_count})`)
    }
  }

  private showFeedback(message: string, color: string) {
    if (this.feedbackText) {
      this.feedbackText.destroy()
    }
    this.feedbackText = this.add.text(400, 100, message, {
      fontSize: '18px',
      color: color
    }).setOrigin(0.5)

    this.time.delayedCall(2000, () => {
      if (this.feedbackText) {
        this.feedbackText.destroy()
        this.feedbackText = null as any
      }
    })
  }

  create() {
    // 创建测试地图 (使用色块)
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

    // 创建玩家 (使用带物理的矩形)
    this.player = this.add.rectangle(125, 125, 30, 30, 0x3498db)
    this.physics.add.existing(this.player)
    this.playerBody = this.player.body as Phaser.Physics.Arcade.Body
    this.playerBody.setCollideWorldBounds(true)

    // 键盘输入
    if (this.input.keyboard) {
      this.cursors = this.input.keyboard.createCursorKeys()
    }

    // UI: 显示玩家状态
    this.showPlayerUI()

    // UI: 区域切换按钮 (左右箭头)
    const leftBtn = this.add.text(20, 540, '◄', {
      fontSize: '24px',
      color: '#ffffff',
      backgroundColor: '#333333'
    }).setInteractive({ useHandCursor: true })
    leftBtn.on('pointerdown', () => this.switchRegion(-1))

    const rightBtn = this.add.text(740, 540, '►', {
      fontSize: '24px',
      color: '#ffffff',
      backgroundColor: '#333333'
    }).setInteractive({ useHandCursor: true })
    rightBtn.on('pointerdown', () => this.switchRegion(1))

    // UI: 当前区域显示
    this.regionText = this.add.text(400, 555, '加载中...', {
      fontSize: '16px',
      color: '#ffffff'
    }).setOrigin(0.5)

    // 加载区域数据
    this.loadRegions()
  }

  update() {
    if (!this.cursors || !this.player) return

    const { left, right, up, down } = this.cursors

    this.playerBody.setVelocity(0)

    if (left.isDown) this.playerBody.setVelocityX(-this.playerSpeed)
    else if (right.isDown) this.playerBody.setVelocityX(this.playerSpeed)

    if (up.isDown) this.playerBody.setVelocityY(-this.playerSpeed)
    else if (down.isDown) this.playerBody.setVelocityY(this.playerSpeed)
  }

  private showPlayerUI() {
    const bg = this.add.graphics()
    bg.fillStyle(0x000000, 0.7)
    bg.fillRect(10, 10, 150, 80)

    this.add.text(20, 20, 'Lv.1', { fontSize: '14px', color: '#ffd700' })
    this.add.text(20, 40, 'HP: 100/100', { fontSize: '14px', color: '#ff6b6b' })
    this.add.text(20, 60, 'Gold: 100', { fontSize: '14px', color: '#ffd700' })
  }
}
