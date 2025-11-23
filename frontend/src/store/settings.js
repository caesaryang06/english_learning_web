import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
    state: () => ({
        voiceName: 'en-US-JennyNeural',
        speechRate: 1.0,
        repeatInterval: 1000
    }),

    actions: {
        setVoiceName(name) {
            this.voiceName = name
            localStorage.setItem('voiceName', name)
        },

        setSpeechRate(rate) {
            this.speechRate = rate
            localStorage.setItem('speechRate', rate.toString())
        },

        setRepeatInterval(interval) {
            this.repeatInterval = interval
            localStorage.setItem('repeatInterval', interval.toString())
        },

        loadFromStorage() {
            const voiceName = localStorage.getItem('voiceName')
            const speechRate = localStorage.getItem('speechRate')
            const repeatInterval = localStorage.getItem('repeatInterval')

            if (voiceName) this.voiceName = voiceName
            if (speechRate) this.speechRate = parseFloat(speechRate)
            if (repeatInterval) this.repeatInterval = parseInt(repeatInterval)
        }
    }
})