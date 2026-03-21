import Phaser from 'phaser'

interface Question {
  id: string
  question: string
  options: string[]
  correct_answer: number
}

export default class BattleScene extends Phaser.Scene {
  private questions: Question[] = []
  private currentQuestionIndex = 0
  private currentQuestion!: Question
  private playerHP = 100
  private playerMaxHP = 100
  private enemyHP = 100
  private enemyMaxHP = 100
  private attackPower = 10
  // 用于更新 UI 的文本对象引用
  private enemyHPText!: Phaser.GameObjects.Text
  private playerHPText!: Phaser.GameObjects.Text
  private questionText!: Phaser.GameObjects.Text
  private optionButtons: Phaser.GameObjects.Text[] = []
  // 捕获相关属性
  private canCapture = false
  private captureAttempted = false
  private captureButton!: Phaser.GameObjects.Text
  // Guest 信息（从外部传入）
  public currentGuest: { id: string; rarity: string } | null = null
  public playerId: string = 'test-player'

  constructor() {
    super({ key: 'BattleScene' })
  }

  init(data: { guestId: string; questions: Question[]; guest?: { id: string; rarity: string }; playerId?: string }) {
    // 数据验证：如果 questions 为空，提供默认问题
    this.questions = data.questions && data.questions.length > 0
      ? data.questions
      : [{
          id: 'default',
          question: 'What is 2 + 2?',
          options: ['3', '4', '5', '6'],
          correct_answer: 1
        }]

    this.currentQuestionIndex = 0
    this.currentQuestion = this.questions[0]
    this.enemyMaxHP = 100
    this.enemyHP = this.enemyMaxHP

    // 设置 Guest 信息
    if (data.guest) {
      this.currentGuest = data.guest
    }
    if (data.playerId) {
      this.playerId = data.playerId
    }
  }

  create() {
    // 战斗背景
    const bg = this.add.graphics()
    bg.fillStyle(0x2a2a4a)
    bg.fillRect(0, 0, 800, 600)

    // 敌方信息
    this.add.text(500, 50, 'Guest', { fontSize: '20px', color: '#fff' })
    this.enemyHPText = this.add.text(500, 80, `HP: ${this.enemyHP}/${this.enemyMaxHP}`, { fontSize: '16px', color: '#ff6b6b' })

    // 玩家信息
    this.add.text(50, 350, 'Player', { fontSize: '20px', color: '#fff' })
    this.playerHPText = this.add.text(50, 380, `HP: ${this.playerHP}/${this.playerMaxHP}`, { fontSize: '16px', color: '#ff6b6b' })

    // 问题显示
    this.questionText = this.add.text(100, 200, this.currentQuestion.question, {
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

    // 创建捕获按钮
    this.captureButton = this.createCaptureButton()
  }

  private createOptionButtons() {
    // 清除旧的按钮
    this.optionButtons.forEach(btn => btn.destroy())
    this.optionButtons = []

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

      this.optionButtons.push(btn)
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
        return
      }
    } else {
      this.playerHP = Math.max(0, this.playerHP - 15)
      this.showFeedback('Wrong!', '#ef4444')

      if (this.playerHP <= 0) {
        this.showDefeat()
        return
      }
    }

    // 不使用 restart，而是更新 UI 和显示下一个问题
    this.updateBattleUI()
  }

  private updateBattleUI() {
    // 更新 HP 显示
    this.enemyHPText.setText(`HP: ${this.enemyHP}/${this.enemyMaxHP}`)
    this.playerHPText.setText(`HP: ${this.playerHP}/${this.playerMaxHP}`)

    // 移动到下一个问题
    this.currentQuestionIndex++

    // 如果还有问题，显示下一个；否则重新开始
    if (this.currentQuestionIndex < this.questions.length) {
      this.currentQuestion = this.questions[this.currentQuestionIndex]
      this.questionText.setText(this.currentQuestion.question)
      this.createOptionButtons()
    } else {
      // 所有问题答完了，重新开始
      this.currentQuestionIndex = 0
      this.currentQuestion = this.questions[0]
      this.questionText.setText(this.currentQuestion.question)
      this.createOptionButtons()
    }
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

    // 战斗胜利后可以捕获
    this.canCapture = true
    this.captureButton.setVisible(true)

    // 2秒后自动返回或等待玩家点击返回
    setTimeout(() => {
      // 不自动返回，等待玩家操作
    }, 2000)
  }

  private createCaptureButton() {
    const btn = this.add.text(400, 450, '捕获', {
      fontSize: '20px',
      backgroundColor: '#4CAF50',
      padding: { x: 20, y: 10 },
      color: '#fff'
    }).setOrigin(0.5)

    btn.setInteractive({ useHandCursor: true })
    btn.on('pointerdown', () => this.attemptCapture())
    btn.setVisible(false)
    return btn
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

  private async attemptCapture() {
    if (!this.canCapture || this.captureAttempted) return

    this.captureAttempted = true
    this.captureButton.setVisible(false)

    const baseRate = 0.6
    const rarityBonus = this.getRarityBonus()
    const success = Math.random() < (baseRate + rarityBonus)

    if (success) {
      this.showFeedback('捕获成功!', '#4ade80')
      // 调用 API 保存捕获
      try {
        await fetch('/api/games/capture', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            anon_id: this.playerId,
            guest_id: this.currentGuest?.id || 'test-guest',
            success: true,
            battle_score: 0
          })
        })
      } catch (e) {
        console.error('捕获保存失败', e)
      }
    } else {
      this.showFeedback('捕获失败...', '#ef4444')
    }

    // 显示返回按钮
    setTimeout(() => {
      this.showReturnToMapOption()
    }, 1500)
  }

  private showReturnToMapOption() {
    const returnBtn = this.add.text(400, 500, '返回地图', {
      fontSize: '18px',
      color: '#88ccff'
    }).setOrigin(0.5)

    returnBtn.setInteractive({ useHandCursor: true })
    returnBtn.on('pointerdown', () => {
      this.scene.start('MapScene')
    })
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
