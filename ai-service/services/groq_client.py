import requests
import os
import json
import time
import redis
import hashlib
from dotenv import load_dotenv
from utils.metrics import response_times

load_dotenv()

# 🔑 API KEY
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 🔥 REDIS SETUP
r = redis.Redis(host='localhost', port=6379, db=0)

def call_groq(prompt):
    # 🔐 CREATE CACHE KEY
    key = hashlib.sha256(prompt.encode()).hexdigest()

    # =========================
    # 🔹 CACHE CHECK
    # =========================
    cached = r.get(key)
    if cached:
        print("CACHE HIT")
        return cached.decode()

    print("CACHE MISS")

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    # =========================
    # 🔁 RETRY LOGIC
    # =========================
    for attempt in range(3):
        try:
            start = time.time()

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=2   # ⚡ performance constraint
            )

            end = time.time()

            # ⏱ TRACK RESPONSE TIME
            response_times.append((end - start) * 1000)

            if response.status_code != 200:
                raise Exception("Bad response")

            result = response.json()
            output_text = result["choices"][0]["message"]["content"]

            # 🧹 CLEAN MARKDOWN
            if output_text.startswith("```"):
                output_text = output_text.strip("```json").strip("```")

            # 💾 STORE IN CACHE (15 min)
            r.setex(key, 900, output_text)

            return output_text

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            time.sleep(1)

    # =========================
    # 🚨 FALLBACK (DAY 9)
    # =========================
    return None