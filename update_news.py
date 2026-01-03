import requests
import os
import json
from datetime import datetime

# Keys laden
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOPIC = "Künstliche Intelligenz"

def get_news():
    print(f"Abfrage NewsAPI für Thema: {TOPIC}...")
    url = f"https://newsapi.org/v2/everything?q={TOPIC}&language=de&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if data.get('status') != 'ok':
            print(f"NewsAPI Fehler: {data.get('message')}")
            return None
        articles = data.get('articles', [])
        return "\n".join([f"Titel: {a['title']}" for a in articles])
    except Exception as e:
        print(f"Fehler bei News-Abruf: {e}")
        return None

def summarize(text):
    if not text:
        return "Keine News gefunden."
    
    print("Sende Daten an Gemini...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts":[{"text": f"Fasse kurz zusammen: {text}"}]}]}
    
    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        
        # Sicherheits-Check: Falls 'candidates' fehlt, stürzt es nicht ab!
        if 'candidates' in res_data:
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            print("--- GEMINI ANTWORT FEHLERHAFT ---")
            print(json.dumps(res_data, indent=2))
            return "KI-Zusammenfassung aktuell nicht verfügbar."
    except Exception as e:
        print(f"Kritischer Fehler im Skript: {e}")
        return "Skript-Fehler."

# Ausführung
news_text = get_news()
summary_result = summarize(news_text)

html_content = f"<html><body><h1>Update {TOPIC}</h1><p>{summary_result}</p></body></html>"
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Fertig! index.html wurde geschrieben.")
