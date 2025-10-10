# نبدأ بصورَة نظيفة ومستقرة
FROM python:3.10-slim-bullseye

# نخبر النظام أنه لا داعي يسألك أسئلة (مهم في الدوكر)
ENV DEBIAN_FRONTEND=noninteractive

# نحدد المكان اللي نشتغل فيه
WORKDIR /app

# نضيف مكان الكود في متغير بايثون
ENV PYTHONPATH=/app/src

# نثبت التبعيات المهمة جدًا
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    gcc \
    g++ \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ننسخ ملف المتطلبات
COPY src/requirements.txt .

# نرفع pip أولًا
RUN pip install --upgrade pip

# 🔥 هنا السر: ننصّب onnxruntime أولًا وبقوة
RUN pip install --force-reinstall --no-cache-dir onnxruntime==1.17.0

# بعد ذلك نثبت باقي المكتبات (مثل unstructured)
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY ./src ./src

# فتح المنفذ 8000
EXPOSE 8000

# تشغيل السيرفر
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]