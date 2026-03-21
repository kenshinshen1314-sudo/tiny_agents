import Phaser from 'phaser'
import MapScene from './scenes/MapScene'
import BattleScene from './scenes/BattleScene'

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: 'game-container',
  backgroundColor: '#1a1a2e',
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { x: 0, y: 0 },
      debug: false
    }
  },
  scene: [MapScene, BattleScene]
}

export function startGame() {
  const game = new Phaser.Game(config)
  return game
}
