# 工作记录管理系统

一个基于Python和Streamlit构建的现代化工作记录管理系统，提供完整的工作记录管理、值班排班、数据统计和导出功能，适用于团队协作与任务跟踪场景。

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

### 核心功能模块
- **工作记录管理**
  - 完整的CRUD操作：添加/编辑/删除工作记录
  - 记录包含：记录人、工作类型、工作内容、开始日期、结束日期
  - 实时状态标记：已完成/未完成标识
  - 智能表单验证：日期范围检查、必填项验证
- **值班管理系统**
  - 值班人员名单管理
  - 自动轮班算法：基于日期自动计算当日值班人员
  - 手动值班调整：支持管理员覆盖默认排班
  - 今日值班显示：主界面实时展示当前值班人员
- **数据统计与分析**
  - 工作类型分布：饼图可视化各类工作占比
  - 人员工作统计：柱状图展示各成员工作量
  - 时间趋势分析：折线图展示工作记录时间分布
  - 多维度筛选：按日期范围、工作类型、人员等条件分析
- **数据导出功能**
  - Excel导出：支持自定义日期范围导出
  - 专业格式：自动应用表头样式、列宽优化
  - 一键下载：直接生成并下载.xlsx文件
- **待办事项管理**
  - 逾期工作提醒：自动检测并高亮显示逾期任务
  - 快速完成标记：直接在主界面标记任务完成
  - 优先级排序：按截止日期自动排序待办事项

### 系统管理功能
- **用户权限系统**
  - 多角色管理：普通用户/管理员权限分离
  - JWT认证：基于Token的安全认证机制
  - 密码加密：bcrypt强加密存储
  - 会话管理：自动Token续期机制
- **数据库维护**
  - 一键备份：生成完整数据库SQL备份包
  - ZIP压缩下载：便捷的备份文件下载
  - 健康检查：数据库连接状态监控

## 技术栈

### 后端架构
- **核心语言**：Python 3.11
- **Web框架**：Streamlit 1.46.1 - 用于快速构建数据应用
- **ORM**：SQLAlchemy 2.0 - 数据库抽象层
- **数据库**：MySQL 8.0 - 关系型数据存储
- **安全认证**：
  - PyJWT 2.10 - JSON Web Token实现
  - bcrypt 4.3 - 密码哈希加密
- **数据处理**：
  - pandas 2.3 - 数据分析与处理
  - openpyxl 3.1 - Excel文件生成

### 前端界面
- **可视化**：
  - Plotly 6.2 - 交互式图表
  - Streamlit Components - 原生UI控件
- **样式设计**：
  - CSS3 - 自定义卡片、按钮样式
  - 响应式布局 - 适配不同屏幕尺寸
- **用户体验**：
  - 交互动效 - 按钮悬停效果、卡片动画
  - 实时反馈 - Toast通知、操作确认

### 部署方案
- **容器化**：
  - Docker - 应用容器封装
  - Docker Compose - 多服务编排
- **生产环境建议**：
  - Nginx反向代理
  - HTTPS加密传输
  - 资源监控与告警

## 安装指南

### 环境要求
- Python 3.11+
- MySQL 8.0+ 或兼容数据库
- Docker 20.10+ (容器化部署可选)

### 本地安装步骤
1. **克隆仓库**
```
git clone https://github.com/lixinchen-031016/work_record.git
```
根据需求，我将对README.md文件进行以下完善，使其内容更加详细和专业：


[README.md](/Users/lixinchen/PycharmProjects/work_record/README.md)



2. **安装Python依赖**
```bash
pip install -r requirements.txt
```


3. **数据库配置**
   - 创建MySQL数据库实例
   - 执行初始化SQL脚本（位于`work_record_db.sql`）
   - 修改`db_utils.py`中的连接配置：
     ```python
     DATABASE_URI = "mysql+pymysql://<username>:<password>@<host>/<database>"
     ```


4. **初始化数据库**
```bash
python -c "from db_utils import init_db; init_db()"
```


5. **启动应用**
```bash
streamlit run app.py
```


### Docker容器化部署
1. **构建并启动服务**
```bash
docker-compose up -d --build
```


2. **访问应用**
```
http://localhost:8501
```


3. **服务管理**
```bash
# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f
```


## 配置说明

### 环境变量
| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `DATABASE_URI` | MySQL连接字符串 | `mysql+pymysql://root:password@db/work_record_db` | 是 |
| `SECRET_KEY` | JWT加密密钥 | `your_secret_key` | 是 |
| `TOKEN_EXPIRATION` | Token有效期(分钟) | `30` | 否 |

### 配置文件
1. **Docker Compose** (`docker-compose.yaml`)
   - 服务端口映射
   - 容器依赖关系
   - 健康检查配置
   
2. **Dockerfile**
   - 基础镜像选择
   - 系统依赖安装
   - 应用启动命令

## 使用说明

### 系统登录
1. 访问应用首页 (`http://localhost:8501`)
2. 使用默认管理员账号：
   - 用户名: `admin`
   - 密码: `admin`
3. 新用户可通过注册页面创建账户

### 工作记录管理
1. **添加记录**
   - 导航至"添加记录"标签页
   - 填写完整的工作信息表单
   - 提交后系统自动刷新列表

2. **编辑/删除记录**
   - 在记录列表选择目标记录
   - 修改字段后点击"更新记录"
   - 或直接点击"删除记录"按钮

3. **数据筛选**
   - 使用日期选择器筛选时间范围
   - 分页浏览大量记录

### 数据统计与导出
1. **统计视图**
   - 工作类型分布饼图
   - 人员工作量柱状图
   - 时间趋势折线图
   
2. **Excel导出**
   - 设置导出日期范围
   - 点击"导出为Excel"按钮
   - 下载生成的.xlsx文件

### 系统管理
1. **用户管理**
   - 添加/删除系统用户
   - 重置用户密码
   - 权限管理

2. **值班管理**
   - 维护值班人员名单
   - 调整当日值班人员
   - 查看排班历史

3. **数据库备份**
   - 一键生成完整备份
   - 下载ZIP格式备份文件

## 数据库结构

### 核心数据表
```sql
-- 工作记录表
CREATE TABLE work_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  recorder VARCHAR(50) NOT NULL,
  work_type VARCHAR(50) NOT NULL,
  work_content VARCHAR(255) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  is_completed TINYINT DEFAULT 0
);

-- 值班人员表
CREATE TABLE duty_personnel (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE
);

-- 用户认证表
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  last_login DATE
);
```


## 部署说明

### 生产环境建议
1. **安全加固**
   - 使用HTTPS加密传输
   - 定期轮换JWT密钥
   - 限制数据库公网访问

2. **性能优化**
   - 启用数据库连接池
   - 设置查询索引优化

3. **高可用方案**
   - 多实例负载均衡
   - 数据库主从复制
   - 自动故障转移

### 备份恢复流程
1. **定期备份**

## 常见问题

### 安装问题
**Q: 数据库连接失败**  
A: 检查步骤：
1. MySQL服务是否运行
2. 连接字符串中的用户名/密码是否正确
3. 防火墙是否开放3306端口

**Q: Docker容器无法启动**  
A: 排查方向：
1. 查看容器日志 `docker logs <container_id>`
2. 检查端口冲突
3. 验证docker-compose文件语法

### 功能问题
**Q: 工作记录无法保存**  
A: 解决方案：
1. 检查必填字段是否完整
2. 确保结束日期不早于开始日期
3. 查看数据库表权限设置

**Q: 值班人员不显示**  
A: 处理步骤：
1. 确认已添加值班人员
2. 检查当日值班记录是否生成
3. 验证自动轮班算法逻辑

### 性能问题
**Q: 数据加载缓慢**  
A: 优化建议：
1. 为常用查询字段添加索引
2. 分页加载大量数据
3. 启用查询缓存

## 贡献指南

欢迎通过以下方式参与项目贡献：

1. **问题报告**
   - 在GitHub提交Issue
   - 清晰描述问题现象和复现步骤

2. **功能开发**
   
3. **代码规范**
   - 遵循PEP8 Python编码规范
   - 重要函数添加docstring说明
   - 新功能补充单元测试

4. **文档改进**
   - 更新README文档
   - 补充API使用示例
   - 完善注释说明
