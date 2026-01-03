import requests
import os
import json
from datetime import datetime

# Keys aus GitHub Secrets laden
NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def start_process():
    print("--- SCHRITT 1: News abrufen ---")
    topic = "Künstliche Intelligenz"
    # News abrufen
    news_url = f"https://newsapi.org/v2/everything?q={topic}&language=de&sortBy=publishedAt&pageSize=5&apiKey={NEWS_KEY}"
    
    try:
        r = requests.get(news_url)
        news_data = r.json()
        if news_data.get('status') != 'ok':
            return f"NewsAPI Fehler: {news_data.get('message')}"
        
        articles = news_data.get('articles', [])
        if not articles:
            return "Keine aktuellen Artikel gefunden."
            
        text_to_summarize = "\n".join([f"Titel: {a['title']}\nInhalt: {a.get('description', '')}" for a in articles])

        print("--- SCHRITT 2: Gemini kontaktieren ---")
        # Korrigierte URL für die stabile V1 API
        gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Fasse diese News-Schlagzeilen kurz und bündig in 3-4 Sätzen zusammen. Nutze Deutsch:\n\n{text_to_summarize}"
                }]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(gemini_url, json=payload, headers=headers)
        res_json = response.json()

        if "candidates" in res_json:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
            return summary
        else:
            print("Vollständige Antwort von Google:", json.dumps(res_json, indent=2))
            return "Die KI konnte die News gerade nicht zusammenfassen (API-Fehler)."

    except Exception as e:
        return f"Ein unerwarteter Fehler ist aufgetreten: {e}"

# Ausführung
result_text = start_process()

# HTML Template
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: auto; background: white; padding: 25px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        h1 {{ color: #1a73e8; font-size: 1.5rem; margin-top: 0; }}
        p {{ white-space: pre-wrap; }}
        .footer {{ margin-top: 20px; font-size: 0.8rem; color: #888; border-top: 1px solid #eee; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Täglich KI-News</h1>
        <p>{result_text}</p>
        <div class="footer">Aktualisiert am: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
