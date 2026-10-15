# 使用带有 Python 3.11 的基础环境
FROM python:3.11-slim

# 后续操作都在 /app 目录中进行
WORKDIR /app

# 复制依赖清单，安装项目需要的库
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY app/ ./app/

# 声明应用使用的端口
EXPOSE 8000

# 启动 FastAPI，允许外部访问
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
