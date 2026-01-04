FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 18080

# 使用 uvicorn 生产级启动
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "18080"]
