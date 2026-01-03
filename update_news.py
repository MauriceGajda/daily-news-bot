import requests
import os
import json
from datetime import datetime

# API Keys aus den GitHub Secrets
NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- DEINE OPTIMIERTE SUCHLISTE ---
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
    "College Corner", "Musste Machen", "Champagner & Chaos", "Leben reicht",
    "Videopodcast", "Videopodcasts", "Talk Now", "TalkNow", "Talk?Now!", "Podcast", "Podcasts"
]

def fetch_news(query, lang='de'):
    url = f"https://newsapi.org/v2/everything?q={query}&language={lang}&sortBy=publishedAt&pageSize=10&apiKey={NEWS_KEY}"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get('articles', [])
    except:
        return []

def start_process():
    # STUFE 1: Spezifische Suche (VIPs & Shows)
    query_spezifisch = " OR ".join([f'"{b}"' for b in MEINE_THEMEN])
    articles = fetch_news(query_spezifisch, 'de')
    status = "Personalisiert"

    # STUFE 2: Branchen-Fallback (Deutsch)
    if not articles:
        articles = fetch_news("Videopodcast OR Podcast-Produktion OR Podcasting", 'de')
        status = "Branchen-Fokus"

    # STUFE 3: Globaler Fallback (Englisch, wird auf Deutsch zusammengefasst)
    if not articles:
        articles = fetch_news("Podcast trends", 'en')
        status = "Global Trends"

    if not articles:
        return "Keine aktuellen News verfügbar.", "Offline"

    # Vorbereitung für KI
    headlines = [f"{a['title']} ({a['source']['name']})" for a in articles]
    text_to_summarize = " \n".join(headlines[:8])

    # Gemini API Call
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Fasse diese News kurz und knackig in 2-3 Sätzen auf Deutsch zusammen. Konzentriere dich auf Medien-Insights. Thema ist {status}:\n\n{text_to_summarize}"}]}]
    }
    
    try:
        response = requests.post(gemini_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
        summary = response.json()['candidates'][0]['content']['parts'][0]['text']
        return summary.strip(), status
    except:
        # Fallback falls KI streikt
        return f"Aktuelle Meldungen aus dem Bereich {status}: " + articles[0]['title'], status

# Daten abrufen
result_text, search_status = start_process()
timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')

# --- DAS DESIGN (DEIN TICKER STYLE) ---
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; background: transparent; font-family: Arial, sans-serif; overflow: hidden; }}
        
        #podcast-news-widget {{
            width: 100%;
            border: 1px solid rgb(255, 236, 192);
            border-radius: 10px;
            background: rgb(0, 21, 56);
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            position: relative;
        }}

        .ticker-header {{
            background: rgb(255, 236, 192);
            color: rgb(0, 21, 56);
            padding: 7px 12px;
            font-weight: bold;
            font-size: 14px;
            display: flex;
            align-items: center;
        }}

        .live-dot {{
            height: 8px;
            width: 8px;
            background-color: #ff0000;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
            animation: pulse-live 2s infinite ease-in-out;
        }}

        #progress-bar-container {{
            width: 100%;
            height: 4px;
            background: rgba(0, 0, 0, 0.2);
        }}

        #progress-bar {{
            width: 100%;
            height: 100%;
            background: linear-gradient(to top, rgb(255, 236, 192) 0%, rgb(204, 189, 154) 100%);
        }}

        #feed-box {{
            padding: 12px 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 50px;
        }}

        .status-info {{
            color: rgb(255, 236, 192);
            opacity: 0.6;
            font-size: 9px;
            text-transform: uppercase;
            margin-bottom: 4px;
            letter-spacing: 0.5px;
        }}

        .ai-summary {{
            color: rgb(255, 236, 192);
            font-size: 13px;
            line-height: 1.4;
            text-align: center;
            margin: 0;
            animation: fadeIn 0.8s ease-out;
        }}

        @keyframes pulse-live {{
            0% {{ opacity: 0.2; transform: scale(0.9); }}
            50% {{ opacity: 1; transform: scale(1.1); }}
            100% {{ opacity: 0.2; transform: scale(0.9); }}
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(3px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @media (max-width: 768px) {{
            #podcast-news-widget {{ border-radius: 0; border-left: none; border-right: none; }}
            .ticker-header {{ justify-content: center; }}
        }}
    </style>
</head>
<body>

<div id="podcast-news-widget">
    <div class="ticker-header">
        <span class="live-dot"></span>
        AI People & Show Tracker
    </div>
    
    <div id="progress-bar-container">
        <div id="progress-bar"></div>
    </div>

    <div id="feed-box">
        <div class="status-info">{search_status} Update | {timestamp}</div>
        <p class="ai-summary">{result_text}</p>
    </div>
</div>

</body>
</html>
"""

# Datei lokal speichern
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
