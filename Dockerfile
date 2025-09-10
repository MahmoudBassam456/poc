# استخدم Python 3.8 slim
FROM python:3.8-slim 

# تعيين working directory
WORKDIR /app

# تثبيت مكتبات النظام المطلوبة لـ OpenCV وبعض المكتبات الأخرى
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف requirements وتنصيبه
COPY src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود المشروع كله
COPY src/ /app/

# expose البورت
EXPOSE 5000

# أمر تشغيل FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
