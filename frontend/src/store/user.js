import { defineStore } from 'pinia'
import { getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null,
        isLoggedIn: false
    }),

    actions: {
        setUser(user) {
            this.user = user
            this.isLoggedIn = true
            localStorage.setItem('user', JSON.stringify(user))
        },

        clearUser() {
            this.user = null
            this.isLoggedIn = false
            localStorage.removeItem('user')
        },

        async checkLogin() {
            try {
                const result = await getCurrentUser()
                if (result.success) {
                    this.setUser(result.user)
                    return true
                } else {
                    this.clearUser()
                    return false
                }
            } catch (error) {
                this.clearUser()
                return false
            }
        },

        loadFromStorage() {
            const userStr = localStorage.getItem('user')
            if (userStr) {
                try {
                    this.user = JSON.parse(userStr)
                    this.isLoggedIn = true
                } catch (e) {
                    this.clearUser()
                }
            }
        }
    }
})