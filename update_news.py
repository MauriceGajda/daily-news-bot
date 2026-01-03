import requests
import os
import json
from datetime import datetime

NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TOPIC = "Künstliche Intelligenz"

def start_process():
    # 1. News abrufen
    news_url = f"https://newsapi.org/v2/everything?q={TOPIC}&language=de&sortBy=publishedAt&pageSize=5&apiKey={NEWS_KEY}"
    
    try:
        r = requests.get(news_url)
        news_data = r.json()
        articles = news_data.get('articles', [])
        
        if not articles:
            return "Heute gibt es keine neuen Schlagzeilen."
        
        # Schlagzeilen für die KI vorbereiten
        headlines = [a['title'] for a in articles]
        text_to_summarize = " \n".join(headlines)

        # 2. Gemini kontaktieren (v1beta Pfad ist für Flash oft stabiler)
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Fasse diese News kurz in 3 Sätzen auf Deutsch zusammen:\n\n{text_to_summarize}"
                }]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(gemini_url, json=payload, headers=headers)
        res_json = response.json()

        # Überprüfung der Antwort
        if "candidates" in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # FALLBACK: Wenn die KI streikt, zeigen wir einfach die Schlagzeilen an!
            print("KI Fehler, nutze Fallback-Liste.")
            fallback_text = "Die KI-Zusammenfassung ist gerade nicht verfügbar. Hier sind die Top-Themen:\n\n"
            for line in headlines:
                fallback_text += f"• {line}\n"
            return fallback_text

    except Exception as e:
        return f"Dienst aktuell nicht erreichbar. Bitte später versuchen."

# HTML Erstellung
result_text = start_process()
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: sans-serif; background-color: #f0f2f5; padding: 20px; display: flex; justify-content: center; }}
        .card {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 500px; width: 100%; }}
        h1 {{ color: #1a73e8; font-size: 1.4rem; margin-top: 0; border-bottom: 2px solid #e8f0fe; padding-bottom: 10px; }}
        p {{ line-height: 1.6; color: #444; white-space: pre-wrap; }}
        .date {{ font-size: 0.75rem; color: #999; margin-top: 20px; text-align: right; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>News Update: {TOPIC}</h1>
        <p>{result_text}</p>
        <div class="date">Aktualisiert: {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr</div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
