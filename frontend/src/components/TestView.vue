<template>
  <div class="test-view" :style="backgroundStyle">
    <!-- 顶部导航栏 -->
    <div class="nav-bar">
      <el-button 
        class="back-btn" 
        @click="confirmBack"
        :icon="ArrowLeft"
        circle
        size="small"
      />
      
      <div class="nav-center">
        <h2>测试模式</h2>
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
      <!-- 类型标签 -->
      <div class="type-badge" :class="`type-${currentItem.type}`">
        {{ getTypeIcon(currentItem.type) }} {{ getTypeName(currentItem.type) }}
      </div>

      <!-- 提示卡片 -->
      <div class="hint-card">
        <div class="chinese">{{ currentItem.chinese }}</div>
        
        <div class="pronunciation" v-if="currentItem.pronunciation">
          🔊 {{ currentItem.pronunciation }}
        </div>
        
        <el-button 
          class="play-btn" 
          @click="playPronunciation"
          circle
        >
          <el-icon :size="20"><VideoPlay /></el-icon>
        </el-button>
      </div>

      <!-- 输入区域 - 改为下划线 -->
      <div class="input-area">
        <!-- 字符输入框模式（单词/短语） - 下划线样式 -->
        <div v-if="currentItem.type !== 'sentence'" class="underline-inputs">
          <div v-for="(word, wordIndex) in wordGroups" :key="wordIndex" class="word-group">
            <div class="char-wrapper" v-for="(char, charIndex) in word" :key="charIndex">
              <input
                v-model="char.value"
                :ref="(el) => setInputRef(el, char.globalIndex)"
                @input="(e) => handleInput(e.target.value, char.globalIndex)"
                @keydown="(e) => handleKeyDown(e, char.globalIndex)"
                class="underline-input"
                maxlength="1"
                type="text"
              />
            </div>
          </div>
        </div>

        <!-- 文本框模式（句子） -->
        <textarea
          v-else
          v-model="sentenceInput"
          class="sentence-input"
          placeholder="请输入完整句子"
          rows="3"
        ></textarea>
      </div>

      <!-- 按钮组 -->
      <div class="button-group">
        <el-button class="action-btn clear-btn" @click="clearInput">
          清空
        </el-button>
        <el-button class="action-btn submit-btn" type="success" @click="submitAnswer">
          提交答案
        </el-button>
      </div>
    </div>

    <!-- 结果对话框保持不变 -->
    <el-dialog v-model="showResult" title="测试结果" width="400px" :show-close="false">
      <div class="result-content">
        <div class="result-icon">{{ accuracy >= 80 ? '🎉' : '💪' }}</div>
        <div class="result-stats">
          <div class="stat-row">
            <span class="stat-label">总题数</span>
            <span class="stat-value">{{ items.length }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">正确数</span>
            <span class="stat-value correct">{{ correctCount }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">错误数</span>
            <span class="stat-value wrong">{{ wrongCount }}</span>
          </div>
          <div class="stat-row highlight">
            <span class="stat-label">正确率</span>
            <span class="stat-value">{{ accuracy }}%</span>
          </div>
        </div>
        <p v-if="wrongItems.length > 0" class="review-hint">
          错误的内容已加入复习库
        </p>
      </div>
      <template #footer>
        <el-button type="primary" @click="goBack" size="large" style="width: 100%">
          返回首页
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, VideoPlay } from '@element-plus/icons-vue'
import { getItemsForTest } from '@/api/items'
import { generateAudio } from '@/api/audio'
import { useSettingsStore } from '@/store/settings'
import { useBackgroundStore } from '@/store/background'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const settingsStore = useSettingsStore()
const backgroundStore = useBackgroundStore()

const items = ref([])
const currentIndex = ref(0)
const inputChars = ref([])
const sentenceInput = ref('')
const inputRefs = ref([])
const correctCount = ref(0)
const wrongCount = ref(0)
const wrongItems = ref([])
const showResult = ref(false)

const currentItem = computed(() => items.value[currentIndex.value] || null)

// 背景样式
const backgroundStyle = computed(() => backgroundStore.getStyle())

// 将字符按单词分组
const wordGroups = computed(() => {
  const words = []
  let currentWord = []
  
  for (const char of inputChars.value) {
    if (char.isSpace) {
      if (currentWord.length > 0) {
        words.push(currentWord)
        currentWord = []
      }
    } else {
      currentWord.push(char)
    }
  }
  
  if (currentWord.length > 0) {
    words.push(currentWord)
  }
  
  return words
})

const accuracy = computed(() => {
  if (items.value.length === 0) return 0
  return ((correctCount.value / items.value.length) * 100).toFixed(1)
})

const getTypeName = (type) => {
  const map = { word: '单词', phrase: '短语', sentence: '句子' }
  return map[type] || '未知'
}

const getTypeIcon = (type) => {
  const map = { word: '📝', phrase: '💬', sentence: '📄' }
  return map[type] || '📌'
}

const setInputRef = (el, index) => {
  if (el) {
    inputRefs.value[index] = el
  }
}

const loadItems = async () => {
  try {
    const result = await getItemsForTest()
    if (result.success) {
      items.value = result.data
      if (items.value.length > 0) {
        initializeInput()
      }
    }
  } catch (error) {
    ElMessage.error('加载失败：' + error.message)
  }
}

const initializeInput = () => {
  if (!currentItem.value) return

  if (currentItem.value.type === 'sentence') {
    sentenceInput.value = ''
  } else {
    const text = currentItem.value.english
    inputChars.value = text.split('').map((char, index) => ({
      value: '',
      isSpace: char === ' ',
      globalIndex: index
    }))
    
    nextTick(() => {
      const firstInput = inputRefs.value.find(ref => ref && !ref.disabled)
      if (firstInput) {
        firstInput.focus()
      }
    })
  }
}

const handleInput = (val, index) => {
  if (val && index < inputChars.value.length - 1) {
    playKeySound()
    
    const nextIndex = inputChars.value.findIndex((c, i) => i > index && !c.isSpace)
    if (nextIndex !== -1 && inputRefs.value[nextIndex]) {
      inputRefs.value[nextIndex].focus()
    }
  }
}

const handleKeyDown = (event, index) => {
  if (event.key === 'Backspace' && !inputChars.value[index].value) {
    let prevIndex = -1
    for (let i = index - 1; i >= 0; i--) {
      if (!inputChars.value[i].isSpace) {
        prevIndex = i
        break
      }
    }
    if (prevIndex !== -1) {
      inputChars.value[prevIndex].value = ''
      inputRefs.value[prevIndex]?.focus()
    }
  }
}

const playKeySound = () => {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)()
  const oscillator = audioContext.createOscillator()
  const gainNode = audioContext.createGain()
  
  oscillator.connect(gainNode)
  gainNode.connect(audioContext.destination)
  
  oscillator.frequency.value = 800
  oscillator.type = 'sine'
  
  gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1)
  
  oscillator.start(audioContext.currentTime)
  oscillator.stop(audioContext.currentTime + 0.1)
}

const playPronunciation = async () => {
  if (!currentItem.value) return
  
  try {
    const audioUrl = await generateAudio(
      currentItem.value.english,
      settingsStore.voiceName,
      settingsStore.speechRate
    )
    const audio = new Audio(audioUrl)
    await audio.play()
  } catch (error) {
    ElMessage.error('播放失败')
  }
}

const clearInput = () => {
  if (currentItem.value.type === 'sentence') {
    sentenceInput.value = ''
  } else {
    inputChars.value.forEach(char => {
      if (!char.isSpace) char.value = ''
    })
    const firstInput = inputRefs.value.find(ref => ref && !ref.disabled)
    if (firstInput) {
      firstInput.focus()
    }
  }
}

const submitAnswer = () => {
  if (!currentItem.value) return

  let userAnswer = ''
  if (currentItem.value.type === 'sentence') {
    userAnswer = sentenceInput.value.trim()
  } else {
    userAnswer = inputChars.value.map(c => c.isSpace ? ' ' : c.value).join('')
  }

  const correctAnswer = currentItem.value.english

  if (userAnswer.toLowerCase() === correctAnswer.toLowerCase()) {
    correctCount.value++
    ElMessage.success('答对了！✓')
  } else {
    wrongCount.value++
    wrongItems.value.push(currentItem.value)
    ElMessageBox.alert(
      `正确答案是：${correctAnswer}`,
      '答错了',
      { type: 'error' }
    )
  }

  nextItem()
}

const nextItem = () => {
  if (currentIndex.value < items.value.length - 1) {
    currentIndex.value++
    initializeInput()
  } else {
    showResult.value = true
  }
}

const confirmBack = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出测试吗？当前进度将不会保存。',
      '确认',
      { type: 'warning' }
    )
    goBack()
  } catch {
    // 用户取消
  }
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  loadItems()
})
</script>

<style scoped>
.test-view {
  height: 100vh;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  background-size: cover;
  background-position: center;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航保持不变 */
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

/* 内容区域 */
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

.hint-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 25px;
  padding: 30px;
  width: 100%;
  max-width: 600px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.chinese {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
}

.pronunciation {
  background: #f3f4f6;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 15px;
  color: #6b7280;
}

.play-btn {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border: none;
  color: white;
  width: 50px;
  height: 50px;
  box-shadow: 0 6px 20px rgba(17, 153, 142, 0.3);
}

.play-btn:hover {
  transform: scale(1.1);
}

/* 下划线输入样式 */
.input-area {
  width: 100%;
  max-width: 800px;
  display: flex;
  justify-content: center;
}

.underline-inputs {
  display: flex;
  flex-wrap: wrap;
  gap: 25px;
  justify-content: center;
  align-items: flex-end;
}

.word-group {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.char-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.underline-input {
  width: 35px;
  height: 40px;
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  text-transform: uppercase;
  border: none;
  border-bottom: 3px solid rgba(255, 255, 255, 0.8);
  background: transparent;
  color: white;
  outline: none;
  transition: all 0.2s ease;
}

.underline-input:focus {
  border-bottom-color: white;
  box-shadow: 0 3px 0 0 rgba(255, 255, 255, 0.3);
}

.sentence-input {
  width: 100%;
  padding: 15px;
  font-size: 16px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.9);
  outline: none;
  resize: none;
  font-family: inherit;
}

.sentence-input:focus {
  border-color: #11998e;
  box-shadow: 0 0 0 3px rgba(17, 153, 142, 0.2);
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 15px;
  flex-shrink: 0;
}

.action-btn {
  padding: 12px 30px;
  font-size: 16px;
  border-radius: 20px;
  font-weight: 600;
  border: none;
  transition: all 0.3s ease;
}

.clear-btn {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.4);
}

.submit-btn {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(17, 153, 142, 0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(17, 153, 142, 0.4);
}

/* 结果对话框样式保持不变 */
.result-content {
  text-align: center;
  padding: 20px;
}

.result-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.stat-row.highlight {
  background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
}

.stat-label {
  font-size: 15px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.stat-value.correct {
  color: #10b981;
}

.stat-value.wrong {
  color: #ef4444;
}

.review-hint {
  font-size: 14px;
  color: #666;
  margin: 15px 0 0 0;
}

/* 响应式 - 移动端每个单词一行 */
@media (max-width: 768px) {
  .underline-inputs {
    flex-direction: column;
    gap: 20px;
    align-items: center;
  }
  
  .word-group {
    justify-content: center;
  }
  
  .hint-card {
    padding: 25px 20px;
  }
  
  .chinese {
    font-size: 24px;
  }
  
  .underline-input {
    width: 32px;
    height: 35px;
    font-size: 20px;
  }
}

@media (max-height: 700px) {
  .hint-card {
    padding: 20px;
    gap: 10px;
  }
  
  .chinese {
    font-size: 24px;
  }
  
  .underline-input {
    width: 30px;
    height: 35px;
    font-size: 20px;
  }
  
  .word-group {
    gap: 6px;
  }
}
</style>