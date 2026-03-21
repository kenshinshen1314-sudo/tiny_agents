import Phaser from 'phaser'

export default class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' })
  }

  preload() {
    // 加载资源 - 使用色块代替图片
  }

  create() {
    this.scene.start('MapScene')
  }
}
