# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装浏览器依赖和其他所需的系统工具
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    fonts-liberation \
    libappindicator3-1 \
    libgbm1 \
    --no-install-recommends \
    && apt-get clean

# 安装 Playwright 及其依赖
RUN pip install --no-cache-dir playwright

# 安装 Chromium 浏览器
RUN python -m playwright install --with-deps

# 复制项目文件到容器内
COPY . /app

# 安装 Python 项目的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露容器的端口（根据实际情况调整）
#EXPOSE 5000

# 设置容器启动时执行的命令
CMD ["python", "xhs_to_tiktok_yuqi.py"]