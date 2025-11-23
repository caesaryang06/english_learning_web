<template>
  <div class="learn-view">
    <!-- 顶部导航栏 - 更紧凑 -->
    <div class="nav-bar">
      <el-button 
        class="back-btn" 
        @click="goBack"
        :icon="ArrowLeft"
        circle
        size="small"
      />
      
      <div class="nav-center">
        <h2>学习模式</h2>
        <span class="progress-text">{{ currentIndex + 1 }} / {{ items.length }}</span>
      </div>
      
      <div class="progress-bar-container">
        <div 
          class="progress-bar-fill" 
          :style="{ width: `${((currentIndex + 1) / items.length) * 100}%` }"
        ></div>
      </div>
    </div>

    <div class="content-wrapper" v-if="currentItem">
      <!-- 类型标签 - 更小 -->
      <div class="type-badge" :class="`type-${currentItem.type}`">
        {{ getTypeIcon(currentItem.type) }} {{ getTypeName(currentItem.type) }}
      </div>

      <!-- 主卡片 - 紧凑布局 -->
      <div class="word-card">
        <!-- 英文 + 音标 -->
        <div class="main-content">
          <h1 class="english">{{ currentItem.english }}</h1>
          <div class="pronunciation" v-if="currentItem.pronunciation">
            🔊 {{ currentItem.pronunciation }}
          </div>
        </div>

        <!-- 分隔线 -->
        <div class="divider"></div>

        <!-- 中文 -->
        <div class="chinese">{{ currentItem.chinese }}</div>

        <!-- 例句 - 紧凑显示 -->
        <div class="examples" v-if="currentItem.example_en">
          <div class="example-row">
            <span class="label">EN</span>
            <span class="text">{{ currentItem.example_en }}</span>
          </div>
          <div class="example-row" v-if="currentItem.example_zh">
            <span class="label">CN</span>
            <span class="text">{{ currentItem.example_zh }}</span>
          </div>
        </div>
      </div>

      <!-- 控制按钮 - 固定在底部 -->
      <div class="controls">
        <el-button 
          class="control-btn" 
          @click="prevItem"
          :icon="ArrowLeftBold"
          circle
          :disabled="currentIndex === 0"
        />
        
        <el-button 
          class="control-btn play-btn" 
          :class="{ playing: isPlaying }"
          @click="togglePlay"
          circle
        >
          <el-icon :size="24">
            <VideoPlay v-if="!isPlaying" />
            <VideoPause v-else />
          </el-icon>
        </el-button>
        
        <el-button 
          class="control-btn" 
          @click="nextItem"
          :icon="ArrowRightBold"
          circle
          :disabled="currentIndex === items.length - 1"
        />
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-else class="loading-state">
      <div class="empty-icon">📚</div>
      <h3>没有学习内容</h3>
      <p>请先导入一些单词、短语或句子</p>
      <el-button type="primary" @click="goBack">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, ArrowLeftBold, ArrowRightBold, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { getItemsForLearning } from '@/api/items'
import { generateAudio } from '@/api/audio'
import { useSettingsStore } from '@/store/settings'
import { ElMessage } from 'element-plus'

const router = useRouter()
const settingsStore = useSettingsStore()

const items = ref([])
const currentIndex = ref(0)
const isPlaying = ref(false)
const audioElement = ref(null)
const playTimer = ref(null)

const currentItem = computed(() => {
  return items.value[currentIndex.value] || null
})

const getTypeName = (type) => {
  const map = { word: '单词', phrase: '短语', sentence: '句子' }
  return map[type] || '未知'
}

const getTypeIcon = (type) => {
  const map = { word: '📝', phrase: '💬', sentence: '📄' }
  return map[type] || '📌'
}

const loadItems = async () => {
  try {
    const result = await getItemsForLearning()
    if (result.success) {
      items.value = result.data
      if (items.value.length === 0) {
        ElMessage.warning('没有可学习的内容')
      }
    }
  } catch (error) {
    ElMessage.error('加载失败：' + error.message)
  }
}

const playAudio = async () => {
  if (!currentItem.value) return
  
  try {
    const audioUrl = await generateAudio(
      currentItem.value.english,
      settingsStore.voiceName,
      settingsStore.speechRate
    )
    
    if (audioElement.value) {
      audioElement.value.pause()
    }
    
    audioElement.value = new Audio(audioUrl)
    await audioElement.value.play()
    
    if (isPlaying.value) {
      playTimer.value = setTimeout(() => {
        if (isPlaying.value) {
          playAudio()
        }
      }, settingsStore.repeatInterval)
    }
  } catch (error) {
    console.error('播放失败:', error)
    ElMessage.error('播放失败')
  }
}

const togglePlay = () => {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    playAudio()
  } else {
    stopAudio()
  }
}

const stopAudio = () => {
  isPlaying.value = false
  if (audioElement.value) {
    audioElement.value.pause()
  }
  if (playTimer.value) {
    clearTimeout(playTimer.value)
    playTimer.value = null
  }
}

const prevItem = () => {
  stopAudio()
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const nextItem = () => {
  stopAudio()
  if (currentIndex.value < items.value.length - 1) {
    currentIndex.value++
  } else {
    ElMessage.success('已学完所有内容！')
    router.push('/')
  }
}

const goBack = () => {
  stopAudio()
  router.push('/')
}

const handleKeyPress = (e) => {
  if (e.key === 'ArrowLeft') {
    prevItem()
  } else if (e.key === 'ArrowRight') {
    nextItem()
  } else if (e.key === ' ') {
    e.preventDefault()
    togglePlay()
  }
}

onMounted(() => {
  loadItems()
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  stopAudio()
  window.removeEventListener('keydown', handleKeyPress)
})
</script>

<style scoped>
.learn-view {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航 - 紧凑 */
.nav-bar {
  position: relative;
  padding: 15px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.nav-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.nav-center h2 {
  margin: 0;
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.progress-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  background: rgba(255, 255, 255, 0.15);
  padding: 4px 12px;
  border-radius: 15px;
}

.progress-bar-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.2);
}

.progress-bar-fill {
  height: 100%;
  background: white;
  transition: width 0.3s ease;
}

/* 内容区域 - 垂直居中 */
.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
}

/* 类型标签 - 紧凑 */
.type-badge {
  padding: 6px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.type-word {
  background: rgba(59, 130, 246, 0.3);
}

.type-phrase {
  background: rgba(16, 185, 129, 0.3);
}

.type-sentence {
  background: rgba(245, 158, 11, 0.3);
}

/* 主卡片 - 固定最大高度 */
.word-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 30px;
  padding: 35px;
  width: 100%;
  max-width: 750px;
  max-height: 65vh;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 主内容区 */
.main-content {
  text-align: center;
}

.english {
  font-size: 42px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 12px 0;
  line-height: 1.2;
  word-wrap: break-word;
}

.pronunciation {
  display: inline-block;
  background: #f3f4f6;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 16px;
  color: #6b7280;
}

.divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #e5e7eb 20%, #e5e7eb 80%, transparent);
  margin: 5px 0;
}

.chinese {
  font-size: 28px;
  font-weight: 600;
  color: #3b82f6;
  text-align: center;
  line-height: 1.4;
}

/* 例句 - 紧凑布局 */
.examples {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 18px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.example-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.example-row .label {
  flex-shrink: 0;
  width: 32px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  color: #6b7280;
}

.example-row .text {
  flex: 1;
  font-size: 15px;
  line-height: 1.6;
  color: #374151;
}

.example-row:last-child .text {
  color: #6b7280;
  font-size: 14px;
}

/* 控制按钮 - 固定位置 */
.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 25px;
  flex-shrink: 0;
  padding-bottom: 10px;
}

.control-btn {
  width: 55px;
  height: 55px;
  border: none;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  color: white;
  transition: all 0.3s ease;
}

.control-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

.control-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.play-btn {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.play-btn:hover {
  transform: scale(1.1);
}

.play-btn.playing {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* 空状态 */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
}

.empty-icon {
  font-size: 70px;
  margin-bottom: 15px;
}

.loading-state h3 {
  font-size: 24px;
  margin: 0 0 8px 0;
}

.loading-state p {
  font-size: 15px;
  opacity: 0.8;
  margin: 0 0 25px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .word-card {
    padding: 25px 20px;
    max-height: 70vh;
  }
  
  .english {
    font-size: 32px;
  }
  
  .chinese {
    font-size: 22px;
  }
  
  .examples {
    padding: 15px;
  }
  
  .example-row .text {
    font-size: 14px;
  }
}

@media (max-height: 700px) {
  .word-card {
    padding: 25px;
    gap: 15px;
  }
  
  .english {
    font-size: 36px;
  }
  
  .chinese {
    font-size: 24px;
  }
}
</style>