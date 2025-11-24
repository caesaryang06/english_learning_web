<template>
  <el-dialog
    v-model="visible"
    title="背景设置"
    width="500px"
    @close="handleClose"
  >
    <div class="background-dialog">
      <el-tabs v-model="activeTab">
        <!-- 渐变背景 -->
        <el-tab-pane label="渐变" name="gradient">
          <div class="tab-content">
            <div class="color-picker-group">
              <div class="picker-item">
                <label>起始颜色</label>
                <el-color-picker v-model="gradientStart" size="large" />
              </div>
              <div class="picker-item">
                <label>结束颜色</label>
                <el-color-picker v-model="gradientEnd" size="large" />
              </div>
            </div>
            
            <div class="preview" :style="gradientPreview">
              预览效果
            </div>
            
            <div class="presets">
              <h4>预设方案</h4>
              <div class="preset-grid">
                <div 
                  v-for="(preset, index) in gradientPresets" 
                  :key="index"
                  class="preset-item"
                  :style="preset.style"
                  @click="applyGradientPreset(preset)"
                >
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 纯色背景 -->
        <el-tab-pane label="纯色" name="color">
          <div class="tab-content">
            <div class="color-picker-group">
              <div class="picker-item">
                <label>背景颜色</label>
                <el-color-picker v-model="solidColor" size="large" />
              </div>
            </div>
            
            <div class="preview" :style="{ background: solidColor }">
              预览效果
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 图片背景 -->
        <el-tab-pane label="图片" name="image">
          <div class="tab-content">
            <el-upload
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleImageChange"
              :show-file-list="false"
              accept="image/*"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽图片到此处 或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 jpg/png 格式，建议尺寸 1920x1080
                </div>
              </template>
            </el-upload>
            
            <div v-if="imagePreview" class="preview" :style="imagePreviewStyle">
              预览效果
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="saveBackground">应用</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { useBackgroundStore } from '@/store/background'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const backgroundStore = useBackgroundStore()

const visible = ref(false)
const activeTab = ref('gradient')
const gradientStart = ref('#667eea')
const gradientEnd = ref('#764ba2')
const solidColor = ref('#667eea')
const imagePreview = ref('')
const imageFile = ref(null)

// 渐变预设
const gradientPresets = [
  { style: { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }, start: '#667eea', end: '#764ba2' },
  { style: { background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' }, start: '#11998e', end: '#38ef7d' },
  { style: { background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }, start: '#f093fb', end: '#f5576c' },
  { style: { background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }, start: '#4facfe', end: '#00f2fe' },
  { style: { background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }, start: '#43e97b', end: '#38f9d7' },
  { style: { background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }, start: '#fa709a', end: '#fee140' },
]

const gradientPreview = computed(() => ({
  background: `linear-gradient(135deg, ${gradientStart.value} 0%, ${gradientEnd.value} 100%)`
}))

const imagePreviewStyle = computed(() => ({
  backgroundImage: `url(${imagePreview.value})`,
  backgroundSize: 'cover',
  backgroundPosition: 'center'
}))

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    // 加载当前设置
    activeTab.value = backgroundStore.type
    gradientStart.value = backgroundStore.gradientStart
    gradientEnd.value = backgroundStore.gradientEnd
    solidColor.value = backgroundStore.solidColor
    imagePreview.value = backgroundStore.imageUrl
  }
})

watch(visible, (val) => { emit('update:modelValue', val) })

const applyGradientPreset = (preset) => {
  gradientStart.value = preset.start
  gradientEnd.value = preset.end
}

const handleImageChange = (file) => {
  imageFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const saveBackground = () => {
  if (activeTab.value === 'gradient') {
    backgroundStore.setGradient(gradientStart.value, gradientEnd.value)
  } else if (activeTab.value === 'color') {
    backgroundStore.setSolidColor(solidColor.value)
  } else if (activeTab.value === 'image') {
    if (imageFile.value) {
      backgroundStore.setImage(imageFile.value)
    } else {
      ElMessage.warning('请先上传图片')
      return
    }
  }
  ElMessage.success('背景已更新')
  handleClose()
}

const handleClose = () => { visible.value = false }
</script>

<style scoped>
.background-dialog {
  padding: 10px;
}

.tab-content {
  padding: 20px 0;
}

.color-picker-group {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.picker-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.picker-item label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.preview {
  height: 150px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.presets h4 {
  font-size: 14px;
  color: #666;
  margin: 0 0 15px 0;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.preset-item {
  height: 60px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 3px solid transparent;
}

.preset-item:hover {
  transform: scale(1.05);
  border-color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.upload-area {
  margin-bottom: 20px;
}
</style>
