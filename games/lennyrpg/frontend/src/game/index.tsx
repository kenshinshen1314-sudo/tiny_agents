import React from 'react'
import Phaser from 'phaser'

class GameScene extends Phaser.Scene {
  constructor() {
    super({ key: 'GameScene' })
  }

  preload() {
    // Placeholder for loading assets
  }

  create() {
    this.add.text(400, 300, 'LennyRPG', {
      fontSize: '48px',
      color: '#ffffff'
    }).setOrigin(0.5)

    this.add.text(400, 360, 'Game Starting...', {
      fontSize: '24px',
      color: '#888888'
    }).setOrigin(0.5)
  }
}

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: 'game-container',
  backgroundColor: '#1a1a2e',
  scene: GameScene
}

class Game extends React.Component {
  private game: Phaser.Game | null = null
  private containerRef: React.RefObject<HTMLDivElement>

  constructor(props: {}) {
    super(props)
    this.containerRef = React.createRef()
  }

  componentDidMount() {
    this.game = new Phaser.Game(config)
  }

  componentWillUnmount() {
    if (this.game) {
      this.game.destroy(true)
    }
  }

  render() {
    return <div id="game-container" ref={this.containerRef} />
  }
}

export default Game
