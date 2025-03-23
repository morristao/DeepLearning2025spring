# 基礎映像：使用精簡版 Python
FROM python:3.9-slim

# 指定容器中的工作目錄
WORKDIR /app

# 複製 requirements 並安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個 app 檔案進容器
COPY . .

# 開放 Flask 預設 port
EXPOSE 5050

# 執行 app.py
CMD ["python", "app.py"]

