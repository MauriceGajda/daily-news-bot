import requests
import os
from datetime import datetime

# Einstellungen
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOPIC = "Künstliche Intelligenz"

def get_news():
    url = f"https://newsapi.org/v2/everything?q={TOPIC}&language=de&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response.get('articles', [])
    return "\n".join([f"Titel: {a['title']}\nInhalt: {a['description']}" for a in articles])

def summarize(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Hier sind aktuelle News zum Thema {TOPIC}. Fasse sie in 3-4 kurzen Sätzen als Update für eine Website zusammen. Nutze einen professionellen Ton:\n\n{text}"
    payload = {"contents": [{"parts":[{"text": prompt}]}]}
    res = requests.post(url, json=payload).json()
    return res['candidates'][0]['content']['parts'][0]['text']

# Workflow
raw_news = get_news()
summary = summarize(raw_news)

# HTML Datei generieren
html = f"""
<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><style>
    body {{ font-family: -apple-system, sans-serif; padding: 20px; color: #333; background: #f9f9f9; }}
    .card {{ background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; }}
    h2 {{ color: #007bff; margin-top: 0; }}
</style></head>
<body>
    <div class="card">
        <h2>News-Update: {TOPIC}</h2>
        <p>{summary}</p>
        <hr>
        <small>Letztes Update: {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr</small>
    </div>
</body>
</html>
"""
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
