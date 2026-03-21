import React from 'react'
import Phaser from 'phaser'
import { startGame } from './index'

class Game extends React.Component {
  private game: Phaser.Game | null = null
  private containerRef: React.RefObject<HTMLDivElement>

  constructor(props: {}) {
    super(props)
    this.containerRef = React.createRef()
  }

  componentDidMount() {
    this.game = startGame()
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
