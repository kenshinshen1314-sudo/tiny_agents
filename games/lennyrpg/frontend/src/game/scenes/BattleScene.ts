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
    this.enemyMaxHP = 100
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
      const damage = Math.floor(20 + this.attackPower * 0.5)
      this.enemyHP = Math.max(0, this.enemyHP - damage)
      this.showFeedback('Correct!', '#4ade80')

      if (this.enemyHP <= 0) {
        this.showVictory()
      }
    } else {
      this.playerHP = Math.max(0, this.playerHP - 15)
      this.showFeedback('Wrong!', '#ef4444')

      if (this.playerHP <= 0) {
        this.showDefeat()
      }
    }

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
    this.add.text(400, 300, 'VICTORY!', {
      fontSize: '48px',
      color: '#ffd700'
    }).setOrigin(0.5)

    setTimeout(() => {
      this.scene.start('MapScene')
    }, 2000)
  }

  private showDefeat() {
    this.add.text(400, 300, 'DEFEATED...', {
      fontSize: '48px',
      color: '#ef4444'
    }).setOrigin(0.5)

    setTimeout(() => {
      this.playerHP = this.playerMaxHP
      this.scene.start('MapScene')
    }, 2000)
  }
}
