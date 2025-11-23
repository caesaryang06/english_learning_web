<template>
  <div class="study-room">
    <div class="room-header">
      <h2>学习室 - {{ roomName }}</h2>
      <div class="online-count">
        <el-icon><User /></el-icon>
        <span>{{ onlineCount }} 人在线</span>
      </div>
    </div>

    <div class="room-content">
      <!-- 学习内容区 -->
      <div class="learn-area">
        <!-- 学习组件 -->
      </div>

      <!-- 聊天区 -->
      <div class="chat-area">
        <div class="messages" ref="messagesContainer">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message"
          >
            <strong>{{ msg.user }}:</strong> {{ msg.message }}
          </div>
        </div>

        <div class="input-area">
          <el-input
            v-model="messageInput"
            placeholder="输入消息..."
            @keyup.enter="sendMessage"
          />
          <el-button type="primary" @click="sendMessage">发送</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { User } from '@element-plus/icons-vue'
import socketService from '@/utils/socket'

const roomName = ref('Room-001')
const username = ref('User' + Math.floor(Math.random() * 1000))
const onlineCount = ref(0)
const messages = ref([])
const messageInput = ref('')
const messagesContainer = ref(null)

onMounted(() => {
  // 连接 WebSocket
  socketService.connect()

  // 加入房间
  socketService.joinRoom(roomName.value, username.value)

  // 监听用户加入
  socketService.on('user_joined', (data) => {
    onlineCount.value = data.user_count
    messages.value.push({
      user: 'System',
      message: `${data.username} 加入了房间`
    })
    scrollToBottom()
  })

  // 监听用户离开
  socketService.on('user_left', (data) => {
    onlineCount.value = data.user_count
    messages.value.push({
      user: 'System',
      message: `${data.username} 离开了房间`
    })
    scrollToBottom()
  })

  // 监听消息
  socketService.on('receive_message', (data) => {
    messages.value.push(data)
    scrollToBottom()
  })

  // 监听进度更新
  socketService.on('progress_updated', (data) => {
    console.log(`${data.user} 的进度: ${data.progress}`)
  })
})

onUnmounted(() => {
  // 离开房间
  socketService.leaveRoom(roomName.value)
  socketService.disconnect()
})

const sendMessage = () => {
  if (messageInput.value.trim()) {
    socketService.sendMessage(roomName.value, messageInput.value)
    messages.value.push({
      user: username.value,
      message: messageInput.value
    })
    messageInput.value = ''
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.study-room {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #409eff;
  color: white;
}

.online-count {
  display: flex;
  align-items: center;
  gap: 8px;
}

.room-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.learn-area {
  background: white;
  border-radius: 10px;
  padding: 20px;
}

.chat-area {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 10px;
  padding: 15px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 15px;
}

.message {
  padding: 8px;
  margin-bottom: 8px;
  background: #f5f5f5;
  border-radius: 5px;
}

.input-area {
  display: flex;
  gap: 10px;
}
</style>
