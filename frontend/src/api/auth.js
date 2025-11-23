import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL

axios.defaults.withCredentials = true

export const register = async (username, email, password) => {
    const response = await axios.post(`${API_BASE}/auth/register`, {
        username,
        email,
        password
    })
    return response.data
}

export const login = async (username, password) => {
    const response = await axios.post(`${API_BASE}/auth/login`, {
        username,
        password
    })
    return response.data
}

export const logout = async () => {
    const response = await axios.post(`${API_BASE}/auth/logout`)
    return response.data
}

export const getCurrentUser = async () => {
    const response = await axios.get(`${API_BASE}/auth/current`)
    return response.data
}

export const updateProfile = async (email, avatar) => {
    const response = await axios.put(`${API_BASE}/auth/profile`, {
        email,
        avatar
    })
    return response.data
}

export const changePassword = async (oldPassword, newPassword) => {
    const response = await axios.put(`${API_BASE}/auth/password`, {
        old_password: oldPassword,
        new_password: newPassword
    })
    return response.data
}