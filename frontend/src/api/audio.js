import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL

export const generateAudio = async (text, voiceName, speechRate) => {
    const response = await axios.post(
        `${API_BASE}/audio/generate`,
        { text, voice_name: voiceName, speech_rate: speechRate },
        { responseType: 'blob' }
    )
    return URL.createObjectURL(response.data)
}

export const getVoices = async () => {
    const response = await axios.get(`${API_BASE}/audio/voices`)
    return response.data
}