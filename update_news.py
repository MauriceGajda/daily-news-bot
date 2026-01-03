import requests
import os
import json
from datetime import datetime

NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- DEINE PERSONEN-LISTE ---
PERSONEN = [
    "Aleks Bechtel", "Alex Schwabe", "Amalie Gölthenboth", "Amy Goodman", 
    "Annabelle Mandeng", "Bambi Mercury", "Britta Kühlmann", "Britta Schewe", 
    "Maurice Gajda", "Charlet C. House", "Gino Bormann", "Chenoa", "Saskia", 
    "Cherin", "Chris Guse", "Daniel Budiman", "Ingo Meß", "Dieter Könnes", 
    "Ewa De Lubomirz", "Fynn Kliemann", "Hannes", "Babo", "Jim Krawall", 
    "Julian F.M. Stoeckel", "Jurassica Parka", "Margot Schlönzke", "Meryl Deep", 
    "Michael Gajda", "Ridal Carel Tchoukuegno", "Sandra Kuhn"
]

# Erstellt die Suchanfrage: "Name 1" OR "Name 2" OR ...
SUCH_QUERY = " OR ".join([f'"{p}"' for p in PERSONEN])

def start_process():
    # Suche in deutschen News, begrenzt auf die letzten 8 Treffer für bessere Übersicht
    news_url = f"https://newsapi.org/v2/everything?q={SUCH_QUERY}&language=de&sortBy=publishedAt&pageSize=8&apiKey={NEWS_KEY}"
    
    try:
        r = requests.get(news_url)
        news_data = r.json()
        articles = news_data.get('articles', [])
        
        if not articles:
            return "Aktuell gibt es keine neuen Pressemeldungen zu den gewählten Personen."
        
        headlines = [f"{a['title']} ({a['source']['name']})" for a in articles]
        text_to_summarize = " \n".join(headlines)

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": f"Fasse die wichtigsten News zu diesen Personen kurz in 3-4 Sätzen auf Deutsch zusammen:\n\n{text_to_summarize}"}]}]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(gemini_url, json=payload, headers=headers)
        res_json = response.json()

        if "candidates" in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # FALLBACK: Liste mit anklickbaren Links
            fallback_html = "Zusammenfassung aktuell nicht verfügbar. Hier sind die neuesten Schlagzeilen:<br><br>"
            for a in articles:
                fallback_html += f"• <a href='{a['url']}' target='_blank' style='color: #1a73e8; text-decoration: none;'>{a['title']}</a> ({a['source']['name']})<br><br>"
            return fallback_html

    except Exception as e:
        return f"Fehler beim Abrufen der Daten."

# HTML Layout
result_text = start_process()
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, sans-serif; background-color: #f8f9fa; padding: 20px; display: flex; justify-content: center; }}
        .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); max-width: 600px; width: 100%; border-top: 5px solid #1a73e8; }}
        h1 {{ color: #1a73e8; font-size: 1.2rem; margin-top: 0; text-transform: uppercase; letter-spacing: 1px; }}
        .content {{ line-height: 1.7; color: #333; }}
        .date {{ font-size: 0.7rem; color: #aaa; margin-top: 25px; text-align: center; font-style: italic; border-top: 1px solid #eee; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>People Tracker Update</h1>
        <div class="content">{result_text}</div>
        <div class="date">Letztes Update am {datetime.now().strftime('%d.%m.%Y um %H:%M')} Uhr</div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
