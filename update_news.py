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

    # KI Zusammenfassung (Extra kurz)
    headlines_text = " \n".join([a['title'] for a in articles[:5]])
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Fasse kurz in MAXIMAL 12 Wörtern zusammen:\n\n{headlines_text}"}]}]}
    
    summary = "Aktuelle Updates aus der Medienwelt."
    try:
        res = requests.post(gemini_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
        summary = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        pass

    ticker_data = [{"title": summary, "is_ai": True}]
    for a in articles[:10]:
        ticker_data.append({"title": a['title'], "url": a['url'], "source": a['source']['name']})
    
    return ticker_data, status

ticker_entries, search_status = start_process()

# --- NEU: ZEITLOGIK FÜR DEN TICKER ---
# Wir speichern die aktuelle Zeit als Timestamp für JavaScript
now_ts = datetime.now().timestamp() * 1000 

# --- HTML MIT DYNAMISCHER ZEITANZEIGE ---
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ margin: 0; padding: 0; background: transparent; font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; }}
        
        #podcast-news-widget {{
            width: 100%; border: 1px solid rgb(255, 236, 192); border-radius: 8px;
            background: rgb(0, 21, 56); overflow: hidden; box-shadow: 0 3px 10px rgba(0,0,0,0.3);
            max-height: 85px;
        }}

        .ticker-header {{
            background: rgb(255, 236, 192); color: rgb(0, 21, 56); padding: 5px 12px;
            font-weight: bold; font-size: 12px; display: flex; align-items: center; 
            height: 22px; position: relative; overflow: hidden;
        }}

        #header-text-container {{ position: relative; height: 100%; width: 100%; display: flex; align-items: center; }}
        
        .header-msg {{
            position: absolute; width: 100%; transition: all 0.6s ease;
            opacity: 0; transform: translateY(10px);
        }}
        .header-msg.active {{ opacity: 1; transform: translateY(0); }}

        .live-dot {{
            height: 6px; width: 6px; background-color: #ff0000; border-radius: 50%;
            margin-right: 8px; flex-shrink: 0; animation: pulse 2s infinite ease-in-out;
        }}

        #progress-bar-container {{ width: 100%; height: 2px; background: rgba(0,0,0,0.2); }}
        #progress-bar {{ width: 0%; height: 100%; background: rgb(255, 236, 192); }}

        #feed-box {{
            padding: 6px 12px; height: 38px; display: flex; flex-direction: column;
            align-items: center; justify-content: center; text-align: center;
        }}

        .status-tag {{ color: rgb(255, 236, 192); opacity: 0.5; font-size: 7px; text-transform: uppercase; margin-bottom: 1px; }}
        
        .news-text {{
            color: rgb(255, 236, 192); font-size: 11px; line-height: 1.2; margin: 0;
            text-decoration: none; font-weight: bold; animation: fadeIn 0.5s;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%; display: block;
        }}

        @keyframes pulse {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(2px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes progress {{ from {{ width: 0%; }} to {{ width: 100%; }} }}

        @media (max-width: 480px) {{
            .news-text {{ font-size: 10px; }}
            .header-msg {{ font-size: 10px; }}
        }}
    </style>
</head>
<body>
    <div id="podcast-news-widget">
        <div class="ticker-header">
            <span class="live-dot"></span>
            <div id="header-text-container">
                <span id="h1" class="header-msg active">Talk?Now! News</span>
                <span id="h2" class="header-msg">Aktuelle News zu Videopodcasts, Medien und unsere Shows</span>
            </div>
        </div>
        <div id="progress-bar-container"><div id="progress-bar"></div></div>
        <div id="feed-box">
            <div id="status" class="status-tag"></div>
            <div id="content-container" style="width: 100%;"></div>
        </div>
    </div>

    <script>
        const entries = {json.dumps(ticker_entries)};
        const updateTime = {now_ts}; 
        let currentIndex = 0;
        
        const box = document.getElementById('content-container');
        const status = document.getElementById('status');
        const bar = document.getElementById('progress-bar');
        
        // Header Wechsel
        const h1 = document.getElementById('h1');
        const h2 = document.getElementById('h2');
        setInterval(() => {{
            if(h1.classList.contains('active')) {{
                h1.classList.remove('active'); h2.classList.add('active');
            }} else {{
                h2.classList.remove('active'); h1.classList.add('active');
            }}
        }}, 4000);

        function getTimeAgo() {{
            const diff = Math.floor((Date.now() - updateTime) / 60000);
            if (diff < 1) return "Gerade eben aktualisiert";
            if (diff === 1) return "Vor 1 Minute aktualisiert";
            return `Vor ${{diff}} Minuten aktualisiert`;
        }}

        function showNext() {{
            const entry = entries[currentIndex];
            bar.style.animation = 'none';
            bar.offsetHeight; 
            bar.style.animation = 'progress 3.5s linear forwards';

            const timeLabel = getTimeAgo();
            status.innerText = entry.is_ai ? `KI-Fokus | ${{timeLabel}}` : `${{entry.source}} | ${{timeLabel}}`;
            
            if (entry.url) {{
                box.innerHTML = `<a href="${{entry.url}}" target="_blank" class="news-text">${{entry.title}}</a>`;
            }} else {{
                box.innerHTML = `<p class="news-text">${{entry.title}}</p>`;
            }}

            currentIndex = (currentIndex + 1) % entries.length;
        }}

        setInterval(showNext, 3500);
        showNext();
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
