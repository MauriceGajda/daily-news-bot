import requests
import os
import json
from datetime import datetime

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
    url = f"https://newsapi.org/v2/everything?q={query}&language={lang}&sortBy=publishedAt&pageSize=15&apiKey={NEWS_KEY}"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get('articles', [])
    except:
        return []

def start_process():
    query_spezifisch = " OR ".join([f'"{b}"' for b in MEINE_THEMEN])
    articles = fetch_news(query_spezifisch, 'de')
    status = "Personalisiert"

    if not articles:
        articles = fetch_news("Videopodcast OR Podcast-Produktion", 'de')
        status = "Branchen-Fokus"

    if not articles:
        return [], "Keine News", status

    # KI Zusammenfassung erstellen
    headlines_text = " \n".join([a['title'] for a in articles[:8]])
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Fasse diese News kurz in 2 Sätzen zusammen:\n\n{headlines_text}"}]}]}
    
    summary = "Aktuelle Updates aus der Welt der Podcasts."
    try:
        res = requests.post(gemini_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
        summary = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        pass

    # Liste für den Ticker aufbereiten
    ticker_data = [{"title": summary, "is_ai": True}]
    for a in articles[:10]:
        ticker_data.append({"title": a['title'], "url": a['url'], "source": a['source']['name']})
    
    return ticker_data, status

ticker_entries, search_status = start_process()
timestamp = datetime.now().strftime('%H:%M')

# --- HTML MIT TICKER-LOGIK ---
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; background: transparent; font-family: Arial, sans-serif; overflow: hidden; }}
        #podcast-news-widget {{
            width: 100%; border: 1px solid rgb(255, 236, 192); border-radius: 10px;
            background: rgb(0, 21, 56); overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        .ticker-header {{
            background: rgb(255, 236, 192); color: rgb(0, 21, 56); padding: 7px 12px;
            font-weight: bold; font-size: 13px; display: flex; align-items: center; white-space: nowrap;
        }}
        .live-dot {{
            height: 8px; width: 8px; background-color: #ff0000; border-radius: 50%;
            margin-right: 10px; animation: pulse 2s infinite ease-in-out;
        }}
        #progress-bar-container {{ width: 100%; height: 3px; background: rgba(0,0,0,0.2); }}
        #progress-bar {{ width: 0%; height: 100%; background: rgb(255, 236, 192); }}
        #feed-box {{
            padding: 10px 15px; height: 50px; display: flex; flex-direction: column;
            align-items: center; justify-content: center; text-align: center;
        }}
        .status-tag {{ color: rgb(255, 236, 192); opacity: 0.6; font-size: 8px; text-transform: uppercase; margin-bottom: 2px; }}
        .news-text {{
            color: rgb(255, 236, 192); font-size: 12px; line-height: 1.3; margin: 0;
            text-decoration: none; font-weight: bold; animation: fadeIn 0.5s;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 0.3; }} 50% {{ opacity: 1; }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(3px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes progress {{ from {{ width: 0%; }} to {{ width: 100%; }} }}
    </style>
</head>
<body>
    <div id="podcast-news-widget">
        <div class="ticker-header">
            <span class="live-dot"></span>
            News rund um Videopodcasts, unsere Shows & Hosts und Talk?Now!
        </div>
        <div id="progress-bar-container"><div id="progress-bar"></div></div>
        <div id="feed-box">
            <div id="status" class="status-tag"></div>
            <div id="content-container"></div>
        </div>
    </div>

    <script>
        const entries = {json.dumps(ticker_entries)};
        let currentIndex = 0;
        const box = document.getElementById('content-container');
        const status = document.getElementById('status');
        const bar = document.getElementById('progress-bar');

        function showNext() {{
            const entry = entries[currentIndex];
            bar.style.animation = 'none';
            bar.offsetHeight; 
            bar.style.animation = 'progress 3s linear forwards';

            status.innerText = entry.is_ai ? "KI-ZUSAMMENFASSUNG | {timestamp}" : (entry.source + " | {timestamp}");
            
            if (entry.url) {{
                box.innerHTML = `<a href="${{entry.url}}" target="_blank" class="news-text">${{entry.title}}</a>`;
            }} else {{
                box.innerHTML = `<p class="news-text">${{entry.title}}</p>`;
            }}

            currentIndex = (currentIndex + 1) % entries.length;
        }}

        setInterval(showNext, 3000);
        showNext();
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
