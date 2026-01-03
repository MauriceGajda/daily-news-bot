import requests
import os
import json
from datetime import datetime

# Keys laden
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOPIC = "Künstliche Intelligenz"

def get_news():
    url = f"https://newsapi.org/v2/everything?q={TOPIC}&language=de&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url).json()
        if response.get('status') != 'ok':
            print(f"DEBUG: NewsAPI Fehler: {response.get('message')}")
            return None
        articles = response.get('articles', [])
        return "\n".join([f"Titel: {a['title']}\nInhalt: {a['description']}" for a in articles])
    except Exception as e:
        print(f"DEBUG: Fehler beim News-Abruf: {e}")
        return None

def summarize(text):
    if not text:
        return "Keine aktuellen News gefunden."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts":[{"text": f"Fasse kurz in 3 Sätzen zusammen:\n\n{text}"}]}]}
    
    response = requests.post(url, json=payload)
    res_data = response.json()
    
    # Das ist die entscheidende Stelle für das Log:
    if 'candidates' not in res_data:
        print("--- KRITISCHER FEHLER VON GEMINI ---")
        print(json.dumps(res_data, indent=2)) # Zeigt uns den echten Grund (z.B. API Key falsch)
        return "Fehler in der KI-Zusammenfassung."

    return res_data['candidates'][0]['content']['parts'][0]['text']

# Ausführung
print("1. Starte News-Abruf...")
raw_news = get_news()
print("2. Sende Daten an Gemini...")
summary = summarize(raw_news)

html_template = f"<html><body style='font-family:sans-serif;'><h2>Update: {TOPIC}</h2><p>{summary}</p></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
print("3. index.html erstellt.")
