import Phaser from 'phaser'

export default class MapScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private playerSpeed = 160

  constructor() {
    super({ key: 'MapScene' })
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

    // 创建玩家 (使用圆形代表)
    this.add.circle(125, 125, 15, 0x3498db)
    this.player = this.physics.add.sprite(125, 125, '') as any
    this.player.setSize(30, 30)
    this.player.setCollideWorldBounds(true)

    // 键盘输入
    if (this.input.keyboard) {
      this.cursors = this.input.keyboard.createCursorKeys()
    }

    // UI: 显示玩家状态
    this.showPlayerUI()
  }

  update() {
    if (!this.cursors || !this.player) return

    const { left, right, up, down } = this.cursors

    this.player.setVelocity(0)

    if (left.isDown) this.player.setVelocityX(-this.playerSpeed)
    else if (right.isDown) this.player.setVelocityX(this.playerSpeed)

    if (up.isDown) this.player.setVelocityY(-this.playerSpeed)
    else if (down.isDown) this.player.setVelocityY(this.playerSpeed)
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
