import requests
import os
import json
from datetime import datetime

NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# HIER DAS NEUE THEMA:
TOPIC = "Videopodcast"

def start_process():
    # Suche nach Videopodcast, sortiert nach den neuesten Treffern
    news_url = f"https://newsapi.org/v2/everything?q={TOPIC}&language=de&sortBy=publishedAt&pageSize=5&apiKey={NEWS_KEY}"
    
    try:
        r = requests.get(news_url)
        news_data = r.json()
        articles = news_data.get('articles', [])
        
        if not articles:
            return "Heute gibt es keine neuen Meldungen zum Thema Videopodcasts."
        
        headlines = [a['title'] for a in articles]
        text_to_summarize = " \n".join(headlines)

        # Versuch mit Gemini Pro (stabilerer Endpunkt)
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": f"Fasse diese News zum Thema {TOPIC} kurz in 3 Sätzen auf Deutsch zusammen:\n\n{text_to_summarize}"}]}]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(gemini_url, json=payload, headers=headers)
        res_json = response.json()

        if "candidates" in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # FALLBACK: Liste mit anklickbaren Links
            print("KI noch im Standby, zeige Link-Liste.")
            fallback_html = "Die KI-Zusammenfassung wird vorbereitet. Hier sind die aktuellen Schlagzeilen:<br><br>"
            for a in articles:
                fallback_html += f"• <a href='{a['url']}' target='_blank' style='color: #1a73e8; text-decoration: none; font-weight: 500;'>{a['title']}</a><br><br>"
            return fallback_html

    except Exception as e:
        return f"Dienst aktuell nicht erreichbar."

# HTML Erstellung (Wichtig: result_text wird jetzt als HTML interpretiert)
result_text = start_process()
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, sans-serif; background-color: #f0f2f5; padding: 20px; display: flex; justify-content: center; }}
        .card {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 550px; width: 100%; }}
        h1 {{ color: #d32f2f; font-size: 1.4rem; margin-top: 0; border-bottom: 2px solid #ffebee; padding-bottom: 10px; }}
        .content {{ line-height: 1.6; color: #444; }}
        .date {{ font-size: 0.75rem; color: #999; margin-top: 20px; text-align: right; border-top: 1px solid #eee; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Update: {TOPIC}</h1>
        <div class="content">{result_text}</div>
        <div class="date">Letzter Scan: {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr</div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
