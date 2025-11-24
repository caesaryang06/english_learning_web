import { defineStore } from 'pinia'

export const useBackgroundStore = defineStore('background', {
    state: () => ({
        type: 'gradient', // 'gradient', 'color', 'image'
        gradientStart: '#667eea',
        gradientEnd: '#764ba2',
        solidColor: '#667eea',
        imageUrl: '',
        imageFile: null
    }),

    actions: {
        setGradient(start, end) {
            this.type = 'gradient'
            this.gradientStart = start
            this.gradientEnd = end
            this.saveToStorage()
        },

        setSolidColor(color) {
            this.type = 'color'
            this.solidColor = color
            this.saveToStorage()
        },

        setImage(file) {
            this.type = 'image'
            this.imageFile = file

            // 读取文件并转为base64
            const reader = new FileReader()
            reader.onload = (e) => {
                this.imageUrl = e.target.result
                this.saveToStorage()
            }
            reader.readAsDataURL(file)
        },

        getStyle() {
            if (this.type === 'gradient') {
                return {
                    background: `linear-gradient(135deg, ${this.gradientStart} 0%, ${this.gradientEnd} 100%)`
                }
            } else if (this.type === 'color') {
                return {
                    background: this.solidColor
                }
            } else if (this.type === 'image' && this.imageUrl) {
                return {
                    backgroundImage: `url(${this.imageUrl})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center'
                }
            }
            return {}
        },

        saveToStorage() {
            localStorage.setItem('background', JSON.stringify({
                type: this.type,
                gradientStart: this.gradientStart,
                gradientEnd: this.gradientEnd,
                solidColor: this.solidColor,
                imageUrl: this.imageUrl
            }))
        },

        loadFromStorage() {
            const saved = localStorage.getItem('background')
            if (saved) {
                try {
                    const data = JSON.parse(saved)
                    this.type = data.type || 'gradient'
                    this.gradientStart = data.gradientStart || '#667eea'
                    this.gradientEnd = data.gradientEnd || '#764ba2'
                    this.solidColor = data.solidColor || '#667eea'
                    this.imageUrl = data.imageUrl || ''
                } catch (e) {
                    console.error('加载背景设置失败', e)
                }
            }
        }
    }
})