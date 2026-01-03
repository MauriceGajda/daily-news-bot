import requests
import os
import json
from datetime import datetime

NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Deine exklusive Liste
MEINE_THEMEN = [
    "Aleks Bechtel", "Alex Schwabe", "Amalie Gölthenboth", "Amy Goodman", "Annabelle Mandeng", 
    "Bambi Mercury", "Britta Kühlmann", "Britta Schewe", "Maurice Gajda", "Charlet C. House", 
    "Gino Bormann", "Chenoa", "Saskia", "Cherin", "Chris Guse", "Daniel Budiman", "Ingo Meß", 
    "Dieter Könnes", "Ewa De Lubomirz", "Fynn Kliemann", "Hannes", "Babo", "Jim Krawall", 
    "Julian F.M. Stoeckel", "Jurassica Parka", "Margot Schlönzke", "Meryl Deep", "Michael Gajda", 
    "Ridal Carel Tchoukuegno", "Sandra Kuhn", "Mischa Lorenz", "Aaron Breyer", "Julia", 
    "Family Affairs", "lemondreams", "German Humour", "Democracy Now!", "Aktivkohle", 
    "Bart & Schnauze", "Cineolux", "Talk? Now! News", "Tagebuch einer Dragqueen", 
    "Überdosis Crime", "Talk Now News Reality", "Übers Podcasten", "Schöne Dinge", 
    "Big Names Only", "Robin Gut", "Catch Me If You Speak", "TMDA", "Jein!", 
    "Stoeckel & Krawall", "Parka & Schlönzke", "Margots Kochtalk", "Margots Schattenkabinett", 
    "Meryl Deep Talk", "Dachboden Revue", "Never Meet Your Idols", "Redlektion", 
    "Gamer By Heart", "Base Talk", "Interior Intim", "Süß & Leiwand", "Busenfreundin", 
    "MGMB", "Gschichten aus der Schwulenbar", "Machgeschichten", "Celebrate Organizations", 
    "College Corner", "Musste Machen", "Champagner & Chaos", "Leben reicht"
]

def fetch_news(query, lang='de'):
    url = f"https://newsapi.org/v2/everything?q={query}&language={lang}&sortBy=publishedAt&pageSize=10&apiKey={NEWS_KEY}"
    r = requests.get(url)
    return r.json().get('articles', [])

def start_process():
    # STUFE 1: Deine Liste
    query_spezifisch = " OR ".join([f'"{b}"' for b in MEINE_THEMEN])
    articles = fetch_news(query_spezifisch, 'de')
    status = "Personalisiert"

    # STUFE 2: Branchen-News (Fallback)
    if not articles:
        print("Stufe 1 leer, suche Branchen-News...")
        articles = fetch_news("Videopodcast OR Podcast-Produktion OR Podcasting", 'de')
        status = "Branchen-Fokus"

    # STUFE 3: Globaler Trend (Sicherheitsnetz)
    if not articles:
        print("Stufe 2 leer, suche globale Podcast-Trends...")
        articles = fetch_news("Podcast", 'en')
        status = "Global Trends"

    if not articles:
        return "Keine aktuellen News verfügbar.", "Offline"

    # KI Zusammenfassung
    headlines = [f"{a['title']} ({a['source']['name']})" for a in articles]
    text_to_summarize = " \n".join(headlines[:8])

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Fasse diese News kurz in 4 Sätzen auf Deutsch zusammen. Thema ist {status}:\n\n{text_to_summarize}"}]}]}
    
    try:
        response = requests.post(gemini_url, json=payload, headers={'Content-Type': 'application/json'})
        summary = response.json()['candidates'][0]['content']['parts'][0]['text']
        return summary, status
    except:
        # Fallback Link-Liste
        html_links = "<br>".join([f"• <a href='{a['url']}'>{a['title']}</a>" for a in articles[:5]])
        return f"Hier sind die aktuellsten Meldungen ({status}):<br>{html_links}", status

# HTML Layout
result_text, search_status = start_process()
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: sans-serif; background: #f0f2f5; padding: 20px; }}
        .card {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 500px; margin: auto; border-top: 6px solid #e91e63; }}
        h1 {{ font-size: 1.2rem; color: #333; margin-bottom: 15px; }}
        .tag {{ display: inline-block; background: #ffebee; color: #e91e63; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-bottom: 10px; }}
        .content {{ line-height: 1.6; color: #444; }}
        .date {{ font-size: 0.7rem; color: #999; margin-top: 20px; text-align: right; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="tag">{search_status}</div>
        <h1>Podcast & Media Update</h1>
        <div class="content">{result_text}</div>
        <div class="date">Aktualisiert: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
