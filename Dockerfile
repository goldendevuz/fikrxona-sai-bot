FROM python:3.12-slim

# ----------------------------
# 1️⃣ System dependencies
# ----------------------------
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# 2️⃣ Copy requirements first for caching
# ----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# 3️⃣ Copy app code
# ----------------------------
COPY . .

# ----------------------------
# 4️⃣ Create non-root user and data folder
# ----------------------------
RUN useradd -m -u 1000 botuser \
    && mkdir -p /app/data \
    && chown -R botuser:botuser /app

# USER botuser

# ----------------------------
# 5️⃣ Set environment DB path to absolute path
# ----------------------------
ENV DB_URL=sqlite+aiosqlite:////app/data/db.sqlite

# ----------------------------
# 6️⃣ Run bot
# ----------------------------
CMD ["python", "bot.py"]
