# 英语学习助手 - 部署文档

## 📋 前置要求

### 本地开发
- Node.js 20+
- Python 3.11+
- MySQL 8.0+

### Docker 部署
- Docker 20.10+
- Docker Compose 2.0+

### 云部署
- Azure 账号（用于 TTS 服务）
- 域名（可选）

---

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

#### 1. 克隆项目
```bash
git clone https://github.com/yourusername/english-learning-web.git
cd english-learning-web
```

#### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入 Azure TTS 配置
```

#### 3. 启动服务
```bash
docker-compose up -d
```

#### 4. 访问应用
- 前端：http://localhost
- 后端 API：http://localhost:5000
- 数据库：localhost:3307

#### 5. 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### 6. 停止服务
```bash
docker-compose down

# 删除数据卷（谨慎操作）
docker-compose down -v
```

---

### 方式二：本地开发

#### 后端设置
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 编辑 config.py 设置数据库连接

# 启动后端
python app.py
```

#### 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

---

## 🌐 云平台部署

### Vercel + Railway（推荐）

#### 前端部署（Vercel）
1. 登录 [Vercel](https://vercel.com)
2. 导入 GitHub 仓库
3. 设置构建命令：
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. 设置环境变量：
   - `VITE_API_URL`: Railway 后端地址
5. 部署

#### 后端部署（Railway）
1. 登录 [Railway](https://railway.app)
2. New Project → Deploy from GitHub
3. 选择仓库的 backend 目录
4. 添加 MySQL 插件
5. 设置环境变量：
   - `DB_HOST`: Railway MySQL 地址
   - `DB_USER`: 数据库用户名
   - `DB_PASSWORD`: 数据库密码
   - `AZURE_TTS_KEY`: Azure API 密钥
   - `AZURE_TTS_REGION`: Azure 区域
6. 部署

---

### AWS 部署

#### 使用 ECS + RDS
```bash
# 1. 构建镜像
docker build -t english-learning-backend ./backend
docker build -t english-learning-frontend ./frontend

# 2. 推送到 ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag english-learning-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/english-learning-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/english-learning-backend:latest

# 3. 创建 ECS 任务定义和服务
# 4. 配置 RDS MySQL 数据库
# 5. 配置 ALB 负载均衡器
```

---

### Azure 部署

#### 使用 App Service
```bash
# 1. 创建资源组
az group create --name english-learning-rg --location eastus

# 2. 创建 MySQL 数据库
az mysql flexible-server create \
  --resource-group english-learning-rg \
  --name english-learning-db \
  --location eastus \
  --admin-user admin_user \
  --admin-password <password>

# 3. 部署后端
az webapp up \
  --resource-group english-learning-rg \
  --name english-learning-api \
  --runtime "PYTHON:3.11" \
  --location eastus

# 4. 部署前端
cd frontend
npm run build
az storage blob upload-batch \
  --destination '$web' \
  --source ./dist \
  --account-name <storage-account>
```

---

## 🔧 配置说明

### 后端配置（backend/config.py）
```python
class Config:
    # 数据库
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_DATABASE = os.getenv('DB_DATABASE', 'english_learning')
    
    # Azure TTS
    AZURE_TTS_KEY = os.getenv('AZURE_TTS_KEY')
    AZURE_TTS_REGION = os.getenv('AZURE_TTS_REGION', 'eastus')
    
    # 其他配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

### 前端配置（frontend/.env）
```bash
# API 地址
VITE_API_URL=http://localhost:5000

# 生产环境
# VITE_API_URL=https://your-api-domain.com
```

---

## 📊 性能优化

### 后端优化
1. **使用 Gunicorn 多进程**
```bash
   gunicorn --workers 4 --threads 2 --timeout 120 app:app
```

2. **启用 Redis 缓存**
```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

3. **数据库连接池**
```python
   pool = mysql.connector.pooling.MySQLConnectionPool(
       pool_name="mypool",
       pool_size=10,
       **db_config
   )
```

### 前端优化
1. **代码分割**
```javascript
   const LearnView = () => import('./components/LearnView.vue')
```

2. **CDN 加速**
```javascript
   // vite.config.js
   build: {
     rollupOptions: {
       external: ['vue', 'element-plus']
     }
   }
```

3. **图片优化**
   - 使用 WebP 格式
   - 懒加载图片

---

## 🔐 安全配置

### HTTPS 配置（Nginx）
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ...其他配置
}
```

### CORS 配置
```python
# backend/app.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### API 密钥安全
- 使用环境变量存储
- 不要提交到 Git
- 定期轮换密钥

---

## 📈 监控和日志

### 应用监控
```python
# 使用 Flask-MonitoringDashboard
pip install flask-monitoringdashboard
```

### 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 数据库备份
```bash
# 每日自动备份
0 2 * * * docker exec english_learning_db mysqldump -u root -p<password> english_learning > /backups/db_$(date +\%Y\%m\%d).sql
```

---

## 🐛 故障排查

### 常见问题

**1. 数据库连接失败**
```bash
# 检查数据库服务
docker-compose ps

# 查看数据库日志
docker-compose logs mysql

# 测试连接
docker exec -it english_learning_db mysql -u root -p
```

**2. 音频生成失败**
- 检查 Azure API 密钥是否正确
- 查看 API 额度是否用完
- 检查网络连接

**3. 前端无法连接后端**
- 检查 CORS 配置
- 验证 API 地址是否正确
- 查看浏览器控制台错误

---

## 📝 维护指南

### 定期任务
- 每周：检查错误日志
- 每月：更新依赖包
- 每季度：审查安全配置
- 每年：续费域名和 SSL 证书

### 更新流程
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose down
docker-compose up -d

# 4. 验证服务
docker-compose ps
```

---

## 📧 技术支持

如遇问题，请通过以下方式联系：
- GitHub Issues
- Email: support@example.com

---

**祝部署顺利！🎉**
````

---