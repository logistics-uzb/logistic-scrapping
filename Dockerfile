# -------- BASE IMAGE --------
FROM python:3.11-slim

# -------- WORKDIR --------
WORKDIR /app

# -------- SYSTEM DEPENDENCIES REQUIRED BY TELETHON --------
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean

# -------- COPY PROJECT FILES --------
COPY . .

# -------- INSTALL PYTHON DEPENDENCIES --------
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# -------- EXPOSE PORT --------
EXPOSE 8000

# -------- START FASTAPI SERVER --------
CMD ["python", "main.py"]
