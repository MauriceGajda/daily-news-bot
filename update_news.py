import requests
import os
from datetime import datetime

# Keys laden
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOPIC = "Künstliche Intelligenz"

def get_news():
    url = f"https://newsapi.org/v2/everything?q={TOPIC}&language=de&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    if response.get('status') != 'ok':
        print(f"--- FEHLER NewsAPI: {response.get('message')} ---")
        return None
    articles = response.get('articles', [])
    return "\n".join([f"Titel: {a['title']}\nInhalt: {a['description']}" for a in articles])

def summarize(text):
    if not text:
        return "Keine aktuellen News zum Thema gefunden."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts":[{"text": f"Fasse diese News kurz in 3 Sätzen zusammen:\n\n{text}"}]}]}
    
    response = requests.post(url, json=payload)
    res_data = response.json()
    
    # Debugging: Zeige die Antwort, falls es schiefgeht
    if 'candidates' not in res_data:
        print(f"--- FEHLER Gemini API Antwort: {res_data} ---")
        return "Zusammenfassung konnte nicht erstellt werden. Siehe Log."

    return res_data['candidates'][0]['content']['parts'][0]['text']

# Ausführung
print("Starte News-Abruf...")
raw_news = get_news()
print("Sende Daten an Gemini...")
summary = summarize(raw_news)

# HTML Datei erstellen
html_template = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: sans-serif; padding: 20px; line-height: 1.6; background: #f4f4f9; }}
        .box {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        h2 {{ color: #2c3e50; margin-top: 0; }}
    </style>
</head>
<body>
    <div class="box">
        <h2>Tägliches Update: {TOPIC}</h2>
        <p>{summary}</p>
        <hr>
        <small>Aktualisiert am: {datetime.now().strftime('%d.%m.%Y %H:%M')}</small>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
print("index.html erfolgreich erstellt.")
