import { io } from 'socket.io-client'

class SocketService {
    constructor() {
        this.socket = null
        this.connected = false
    }

    connect(url = 'http://localhost:5001') {
        this.socket = io(url, {
            transports: ['websocket'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 5
        })

        this.socket.on('connect', () => {
            console.log('WebSocket connected')
            this.connected = true
        })

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected')
            this.connected = false
        })

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error)
        })

        return this.socket
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect()
            this.socket = null
            this.connected = false
        }
    }

    // 加入学习室
    joinRoom(room, username) {
        if (this.socket) {
            this.socket.emit('join_study_room', { room, username })
        }
    }

    // 离开学习室
    leaveRoom(room) {
        if (this.socket) {
            this.socket.emit('leave_study_room', { room })
        }
    }

    // 同步进度
    syncProgress(room, progress) {
        if (this.socket) {
            this.socket.emit('sync_progress', { room, progress })
        }
    }

    // 发送消息
    sendMessage(room, message) {
        if (this.socket) {
            this.socket.emit('send_message', { room, message })
        }
    }

    // 请求帮助
    requestHelp(room, word) {
        if (this.socket) {
            this.socket.emit('request_help', { room, word })
        }
    }

    // 监听事件
    on(event, callback) {
        if (this.socket) {
            this.socket.on(event, callback)
        }
    }

    // 移除监听
    off(event, callback) {
        if (this.socket) {
            this.socket.off(event, callback)
        }
    }
}

export default new SocketService()