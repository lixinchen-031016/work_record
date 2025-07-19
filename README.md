# 工作记录管理系统

一个基于Python和Streamlit构建的工作记录管理系统，提供工作记录管理、值班人员排班、数据统计和导出等功能。

## 目录
- [功能特点](#功能特点)
- [技术栈](#技术栈)
- [安装指南](#安装指南)
- [配置说明](#配置说明)
- [使用说明](#使用说明)
- [数据库结构](#数据库结构)
- [API文档](#api文档)
- [部署说明](#部署说明)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)


## 功能特点

### 核心功能
- **工作记录管理**
  - 添加/编辑/删除工作记录
  - 记录包含：记录人、工作类型、工作内容、开始日期、结束日期
  - 标记工作完成状态
- **值班管理**
  - 值班人员管理
  - 自动值班轮换
  - 手动调整值班人员
- **数据统计**
  - 工作类型分布分析
  - 记录人工作统计
  - 时间分布趋势图表
- **数据导出**
  - 按日期范围导出Excel
  - 自定义导出格式
- **待办事项**
  - 显示未完成工作
  - 逾期工作提醒

### 系统管理
- **用户管理**
  - 用户注册/登录
  - 密码修改
  - 管理员权限
- **数据库备份**
  - 一键备份所有数据
  - 下载完整SQL备份

## 技术栈

### 后端
- Python 3.11
- Streamlit (Web框架)
- SQLAlchemy (ORM)
- MySQL (数据库)
- PyJWT (认证)
- bcrypt (密码加密)

### 前端
- Streamlit UI组件
- Plotly (图表)
- OpenPyXL (Excel导出)
- 自定义CSS样式

### 部署
- Docker容器化
- Docker Compose编排

## 安装指南

### 前提条件
- Python 3.11+
- MySQL 8.0+
- Docker (可选)

### 本地安装
1. 克隆仓库
```bash
git clone https://github.com/lixinchen-031016/work_record.git
```
2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```


3. 配置数据库
   - 创建MySQL数据库 `work_record_db`
   - 修改`db_utils.py`中的数据库连接配置

4. 初始化数据库
   ```bash
   python -c "from db_utils import init_db; init_db()"
   ```


5. 运行应用
   ```bash
   streamlit run app.py
   ```


### Docker安装
1. 构建并启动容器
   ```bash
   docker-compose up -d
   ```


2. 访问应用
   ```
   http://localhost:8501
   ```


## 配置说明

### 环境变量
| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| DATABASE_URI | MySQL连接URI | mysql+pymysql://root:password@db/work_record_db |
| SECRET_KEY | JWT加密密钥 | your_secret_key |

### 配置文件
- `docker-compose.yaml`: 容器配置
- `Dockerfile`: 应用镜像构建配置

## 使用说明

1. **登录系统**
   - 默认管理员账号: admin/admin
   - 新用户需先注册

2. **主界面功能**
   - 顶部导航栏切换工作记录和系统管理
   - 左侧边栏显示待办事项提醒
   - 值班人员卡片显示今日值班

3. **工作记录操作**
   - 添加: 填写完整表单提交
   - 编辑: 选择记录后修改
   - 删除: 选择记录后删除

4. **数据导出**
   - 选择日期范围
   - 点击"导出为Excel"按钮

5. **系统管理**
   - 用户管理: 添加/删除/修改用户
   - 值班管理: 维护值班人员名单
   - 数据库备份: 下载完整备份

## 数据库结构

### 主要表结构
- `work_records`: 工作记录表
- `duty_personnel`: 值班人员表
- `daily_duties`: 每日值班记录
- `users`: 系统用户表

详细SQL结构见`work_record_db.sql`

## API文档

### 认证API
- `POST /login`: 用户登录
- `POST /register`: 用户注册

### 工作记录API
- `GET /records`: 获取记录列表
- `POST /records`: 添加新记录
- `PUT /records/{id}`: 更新记录
- `DELETE /records/{id}`: 删除记录

## 部署说明

### 生产环境建议
1. 使用Nginx反向代理
2. 配置HTTPS证书
3. 定期数据库备份
4. 监控系统资源使用

### 备份恢复
1. 使用系统内置备份功能
2. 或手动备份MySQL数据目录

## 常见问题

Q: 无法连接到数据库
A: 检查数据库服务是否运行，连接配置是否正确

Q: 导出功能报错
A: 确保服务器有写入权限，磁盘空间充足

Q: 值班人员不显示
A: 检查是否已添加值班人员

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交Pull Request
