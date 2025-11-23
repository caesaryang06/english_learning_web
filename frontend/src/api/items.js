import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL
export const getStatistics = async () => {
    const response = await axios.get(`${API_BASE}/items/statistics`)
    return response.data
}

export const getItemsForLearning = async (limit = 50) => {
    const response = await axios.get(`${API_BASE}/items/list`, { params: { limit } })
    return response.data
}

export const getItemsForTest = async (limit = 20) => {
    const response = await axios.get(`${API_BASE}/items/test`, { params: { limit } })
    return response.data
}

export const importItems = async (type, items) => {
    const response = await axios.post(`${API_BASE}/items/import`, { type, items })
    return response.data
}