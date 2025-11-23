<template>
  <el-dialog
    v-model="visible"
    title="应用设置"
    width="550px"
    @close="handleClose"
  >
    <div class="settings-dialog">
      <!-- 发音人选择 -->
      <div class="setting-item">
        <label>发音人：</label>
        <el-select v-model="localSettings.voiceName" placeholder="选择发音人">
          <el-option
            v-for="(value, label) in voices"
            :key="value"
            :label="label"
            :value="value"
          />
        </el-select>
      </div>

      <!-- 语速设置 -->
      <div class="setting-item">
        <label>语音速度：<span class="value">{{ localSettings.speechRate.toFixed(1) }}x</span></label>
        <el-slider
          v-model="localSettings.speechRate"
          :min="0.5"
          :max="2.0"
          :step="0.1"
          :marks="{ 0.5: '0.5x', 1.0: '1.0x', 2.0: '2.0x' }"
        />
        <div class="tip">范围: 0.5x (慢) ~ 2.0x (快)</div>
      </div>

      <!-- 重复间隔设置 -->
      <div class="setting-item">
        <label>重复间隔：<span class="value">{{ localSettings.repeatInterval }}ms</span></label>
        <el-slider
          v-model="localSettings.repeatInterval"
          :min="500"
          :max="5000"
          :step="100"
          :marks="{ 500: '0.5s', 2500: '2.5s', 5000: '5.0s' }"
        />
        <div class="tip">范围: 500ms (0.5秒) ~ 5000ms (5秒)</div>
      </div>

      <!-- 测试按钮 -->
      <div class="test-section">
        <el-button type="primary" @click="testSpeech" :loading="testing">
          🔊 测试发音
        </el-button>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="saveSettings">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, reactive } from 'vue'
import { useSettingsStore } from '@/store/settings'
import { generateAudio } from '@/api/audio'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const settingsStore = useSettingsStore()
const visible = ref(false)
const testing = ref(false)

const voices = {
  "Jenny (女声-自然)": "en-US-JennyNeural",
  "Guy (男声-自然)": "en-US-GuyNeural",
  "Aria (女声-活泼)": "en-US-AriaNeural",
  "Davis (男声-沉稳)": "en-US-DavisNeural",
  "Jane (女声-优雅)": "en-US-JaneNeural",
  "Jason (男声-专业)": "en-US-JasonNeural",
  "Sara (女声-温柔)": "en-US-SaraNeural",
  "Tony (男声-友好)": "en-US-TonyNeural"
}

const localSettings = reactive({
  voiceName: settingsStore.voiceName,
  speechRate: settingsStore.speechRate,
  repeatInterval: settingsStore.repeatInterval
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    // 对话框打开时，重置为当前设置
    localSettings.voiceName = settingsStore.voiceName
    localSettings.speechRate = settingsStore.speechRate
    localSettings.repeatInterval = settingsStore.repeatInterval
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const testSpeech = async () => {
  testing.value = true
  try {
    const audioUrl = await generateAudio(
      "Hello, this is a test.",
      localSettings.voiceName,
      localSettings.speechRate
    )
    const audio = new Audio(audioUrl)
    await audio.play()
  } catch (error) {
    ElMessage.error('测试失败')
  } finally {
    testing.value = false
  }
}

const saveSettings = () => {
  settingsStore.setVoiceName(localSettings.voiceName)
  settingsStore.setSpeechRate(localSettings.speechRate)
  settingsStore.setRepeatInterval(localSettings.repeatInterval)
  ElMessage.success('设置已保存！')
  handleClose()
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.settings-dialog {
  padding: 10px;
}

.setting-item {
  margin-bottom: 35px;
}

.setting-item label {
  display: block;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 500;
}

.setting-item .value {
  float: right;
  color: #909399;
  font-size: 14px;
}

.tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.test-section {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>
