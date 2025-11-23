<template>
  <el-dialog
    v-model="visible"
    title="导入学习内容"
    width="650px"
    @close="handleClose"
  >
    <div class="import-dialog">
      <!-- 类型选择 -->
      <div class="type-section">
        <h3>选择导入类型：</h3>
        <el-radio-group v-model="importType" size="large">
          <el-radio label="word">单词 (Word)</el-radio>
          <el-radio label="phrase">短语 (Phrase)</el-radio>
          <el-radio label="sentence">句子 (Sentence)</el-radio>
        </el-radio-group>
      </div>

      <!-- 格式说明 -->
      <div class="format-section">
        <h3>文件格式说明：</h3>
        <el-scrollbar height="280px">
          <div class="format-text">
            <p>每行一条记录，使用 | 分隔字段：</p>
            <p><strong>格式：</strong>英文|中文|音标|英文例句|中文例句</p>
            
            <h4>示例：</h4>
            <ul>
              <li><strong>单词：</strong><br>
                hello|你好|/həˈləʊ/|Hello, nice to meet you.|你好，很高兴见到你。
              </li>
              <li><strong>短语：</strong><br>
                take care of|照顾|/teɪk keə ɒv/|I will take care of it.|我会处理的。
              </li>
              <li><strong>句子：</strong><br>
                How are you?|你好吗？||How are you doing today?|你今天过得怎么样？
              </li>
            </ul>

            <h4>注意：</h4>
            <ul>
              <li>音标可以为空</li>
              <li>例句为可选项</li>
              <li>使用UTF-8编码保存文件</li>
            </ul>
          </div>
        </el-scrollbar>
      </div>

      <!-- 文件上传 -->
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          accept=".txt"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处 或 <em>点击选择文件</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">只支持 .txt 文件</div>
          </template>
        </el-upload>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleImport" :loading="importing">
        开始导入
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { importItems } from '@/api/items'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'refresh'])

const visible = ref(false)
const importType = ref('word')
const uploadRef = ref()
const currentFile = ref(null)
const importing = ref(false)

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleFileChange = (file) => {
  currentFile.value = file.raw
}

const parseFile = (content) => {
  const lines = content.split('\n')
  const items = []
  
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    
    const parts = trimmed.split('|')
    if (parts.length >= 2) {
      items.push({
        english: parts[0]?.trim() || '',
        chinese: parts[1]?.trim() || '',
        pronunciation: parts[2]?.trim() || '',
        example_en: parts[3]?.trim() || '',
        example_zh: parts[4]?.trim() || ''
      })
    }
  }
  
  return items
}

const handleImport = async () => {
  if (!currentFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  importing.value = true

  try {
    const reader = new FileReader()
    
    reader.onload = async (e) => {
      try {
        const content = e.target.result
        const items = parseFile(content)
        
        if (items.length === 0) {
          ElMessage.warning('文件中没有有效数据')
          importing.value = false
          return
        }

        const result = await importItems(importType.value, items)
        
        if (result.success) {
          ElMessage.success(`成功导入 ${result.count} 条记录！`)
          emit('refresh')
          handleClose()
        }
      } catch (error) {
        ElMessage.error('导入失败：' + error.message)
      } finally {
        importing.value = false
      }
    }

    reader.onerror = () => {
      ElMessage.error('文件读取失败')
      importing.value = false
    }

    reader.readAsText(currentFile.value, 'UTF-8')
  } catch (error) {
    ElMessage.error('导入出错：' + error.message)
    importing.value = false
  }
}

const handleClose = () => {
  visible.value = false
  uploadRef.value?.clearFiles()
  currentFile.value = null
  importing.value = false
}
</script>

<style scoped>
.import-dialog {
  padding: 10px;
}

.type-section {
  margin-bottom: 25px;
}

.type-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.format-section {
  margin-bottom: 25px;
}

.format-section h3 {
  margin-bottom: 10px;
  font-size: 16px;
}

.format-text {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.8;
}

.format-text h4 {
  margin: 15px 0 8px 0;
  font-size: 14px;
  color: #409eff;
}

.format-text ul {
  padding-left: 20px;
}

.format-text li {
  margin: 8px 0;
}

.upload-section {
  margin-top: 20px;
}
</style>