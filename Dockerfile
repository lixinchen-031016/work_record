# 使用更轻量的Python官方镜像
FROM python:3.11-alpine

# 设置工作目录
WORKDIR /app

# 先复制requirements.txt单独安装依赖
COPY requirements.txt .

# 安装系统依赖和Python包
RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev && \
    pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ && \
    apk del gcc musl-dev

# 复制其余文件
COPY . .

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8501/_stcore/health || exit 1

# 启动命令
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]