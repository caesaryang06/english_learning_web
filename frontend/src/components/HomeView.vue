<template>
  <div class="home-view" :style="backgroundStyle">
    <!-- 用户信息栏 -->
    <div class="user-bar">
      <div class="user-info">
        <el-avatar :size="40" class="avatar">
          {{ user?.username?.charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="user-details">
          <span class="username">{{ user?.username }}</span>
          <span class="user-role">学习者</span>
        </div>
      </div>
      <el-button 
        class="logout-btn" 
        @click="handleLogout"
        size="small"
      >
        退出
      </el-button>
    </div>

    <div class="content-wrapper">
      <!-- Logo 图标 -->
      <div class="logo-icon">📚</div>

      <!-- 标题区域 - 紧凑 -->
      <div class="title-section">
        <h1 class="main-title">英语学习助手</h1>
        <p class="subtitle">English Learning Companion</p>
      </div>

      <!-- 主功能卡片 - 横向紧凑 -->
      <div class="main-cards">
        <div class="card learn-card" @click="$router.push('/learn')">
          <div class="card-icon">📖</div>
          <div class="card-info">
            <h3>学习模式</h3>
            <p>Learn Mode</p>
            <span class="card-desc">沉浸式学习体验</span>
          </div>
          <div class="card-arrow">→</div>
        </div>

        <div class="card test-card" @click="$router.push('/test')">
          <div class="card-icon">✍️</div>
          <div class="card-info">
            <h3>测试模式</h3>
            <p>Test Mode</p>
            <span class="card-desc">检验学习成果</span>
          </div>
          <div class="card-arrow">→</div>
        </div>
      </div>

      <!-- 统计卡片 - 紧凑 -->
      <div class="stats-card">
        <div class="stat-item">
          <div class="stat-icon">📝</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.word_count }}</span>
            <span class="stat-label">单词</span>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon">💬</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.phrase_count }}</span>
            <span class="stat-label">短语</span>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon">📄</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.sentence_count }}</span>
            <span class="stat-label">句子</span>
          </div>
        </div>
        
        <div class="stat-item highlight">
          <div class="stat-icon">🔥</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.today_learned }}</span>
            <span class="stat-label">今日学习</span>
          </div>
        </div>
      </div>

      <!-- 快捷操作 - 紧凑 -->
      <div class="action-cards">
        <div class="action-card" @click="showImportDialog = true">
          <span class="action-icon">📥</span>
          <span class="action-text">导入内容</span>
        </div>
        <div class="action-card" @click="showSettingsDialog = true">
          <span class="action-icon">⚙️</span>
          <span class="action-text">设置</span>
        </div>
      </div>
    </div>

    <!-- 对话框 -->
    <ImportDialog v-model="showImportDialog" @refresh="loadStatistics" />
    <SettingsDialog v-model="showSettingsDialog" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { logout } from '@/api/auth'
import { getStatistics } from '@/api/items'
import ImportDialog from './ImportDialog.vue'
import SettingsDialog from './SettingsDialog.vue'
import { ElMessage } from 'element-plus'
import { useBackgroundStore } from '@/store/background'

const router = useRouter()
const userStore = useUserStore()

const user = computed(() => userStore.user)

const stats = ref({
  word_count: 0,
  phrase_count: 0,
  sentence_count: 0,
  today_learned: 0
})

const showImportDialog = ref(false)
const showSettingsDialog = ref(false)

const handleLogout = async () => {
  try {
    await logout()
    userStore.clearUser()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出失败')
  }
}

const loadStatistics = async () => {
  const result = await getStatistics()
  if (result.success) {
    stats.value = result.data
  }
}

onMounted(() => {
  loadStatistics()
})

const backgroundStore = useBackgroundStore()
const backgroundStyle = computed(() => backgroundStore.getStyle())
</script>

<style scoped>
.home-view {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 用户信息栏 - 紧凑 */
.user-bar {
  position: absolute;
  top: 20px;
  right: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 10;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 6px 15px 6px 6px;
  border-radius: 40px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-weight: bold;
  font-size: 16px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  color: white;
  font-weight: 600;
  font-size: 14px;
  line-height: 1;
}

.user-role {
  color: rgba(255, 255, 255, 0.7);
  font-size: 11px;
  margin-top: 2px;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 18px;
  padding: 8px 16px;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* 内容区域 - 垂直居中 */
.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 70px 30px 30px;
  gap: 25px;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

/* Logo 图标 */
.logo-icon {
  font-size: 50px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* 标题区域 - 紧凑 */
.title-section {
  text-align: center;
}

.main-title {
  font-size: 38px;
  color: white;
  margin: 0 0 6px 0;
  font-weight: 700;
}

.subtitle {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  letter-spacing: 1px;
}

/* 主功能卡片 - 紧凑横向 */
.main-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
  width: 100%;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
}

.card-info h3 {
  font-size: 20px;
  color: #333;
  margin: 0 0 4px 0;
  font-weight: 600;
}

.card-info p {
  font-size: 12px;
  color: #999;
  margin: 0 0 6px 0;
}

.card-desc {
  font-size: 11px;
  color: #666;
  background: #f5f5f5;
  padding: 3px 10px;
  border-radius: 10px;
  display: inline-block;
}

.card-arrow {
  font-size: 24px;
  color: #999;
  transition: transform 0.3s ease;
}

.card:hover .card-arrow {
  transform: translateX(4px);
}

/* 统计卡片 - 紧凑 */
.stats-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 18px 25px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 100%;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  gap: 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 15px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: #f8f9fa;
}

.stat-item.highlight {
  background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
}

.stat-icon {
  font-size: 26px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 11px;
  color: #666;
  margin-top: 3px;
}

/* 快捷操作 - 横向紧凑 */
.action-cards {
  display: flex;
  gap: 15px;
  width: 100%;
}

.action-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 18px;
  padding: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-3px);
}

.action-icon {
  font-size: 28px;
}

.action-text {
  color: white;
  font-size: 15px;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 60px 20px 20px;
    gap: 20px;
  }
  
  .main-title {
    font-size: 32px;
  }
  
  .main-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-card {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-height: 700px) {
  .logo-icon {
    font-size: 40px;
  }
  
  .main-title {
    font-size: 32px;
  }
  
  .card {
    padding: 20px;
  }
  
  .stats-card {
    padding: 15px 20px;
  }
  
  .content-wrapper {
    gap: 18px;
  }
}
</style>