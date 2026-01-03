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
    news_url = f"https://newsapi.org/v2/everything?q={topic}&language=de&sortBy=publishedAt&pageSize=3&apiKey={NEWS_KEY}"
    
    try:
        r = requests.get(news_url)
        news_data = r.json()
        if news_data.get('status') != 'ok':
            print(f"NewsAPI Fehler: {news_data.get('message')}")
            return "Fehler beim Laden der News."
        
        articles = news_data.get('articles', [])
        text_to_summarize = "\n".join([a['title'] for a in articles])
        print(f"News gefunden: {len(articles)} Artikel")

        print("--- SCHRITT 2: Gemini kontaktieren ---")
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts":[{"text": f"Fasse das kurz zusammen: {text_to_summarize}"}]}]}
        
        response = requests.post(gemini_url, json=payload)
        res_json = response.json()

        # SICHERHEITS-CHECK statt Zeile 21 Absturz
        if "candidates" in res_json:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
            print("Zusammenfassung erfolgreich erstellt.")
            return summary
        else:
            print("--- KRITISCHER FEHLER: Gemini hat keine 'candidates' geliefert ---")
            print("Vollständige Antwort von Google:", json.dumps(res_json, indent=2))
            return "Die KI konnte die News gerade nicht zusammenfassen."

    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return "Systemfehler."

# Ausführung und Speichern
result_text = start_process()
html_content = f"<html><body><h1>News Update</h1><p>{result_text}</p></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("--- SCHRITT 3: index.html wurde gespeichert ---")
