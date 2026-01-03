import requests
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import email.utils

NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- DEINE THEMENLISTE ---
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

def fetch_news_api(query):
    url = f"https://newsapi.org/v2/everything?q={query}&language=de&sortBy=publishedAt&pageSize=20&apiKey={NEWS_KEY}"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get('articles', [])
    except: return []

def fetch_google_news(query):
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=de&gl=DE&ceid=DE:de"
    google_articles = []
    limit_date = datetime.now() - timedelta(days=30)
    try:
        r = requests.get(rss_url, timeout=10)
        root = ET.fromstring(r.content)
        for item in root.findall('.//item'):
            pub_date_str = item.find('pubDate').text
            pub_date_parsed = email.utils.parsedate_to_datetime(pub_date_str)
            if pub_date_parsed.replace(tzinfo=None) > limit_date:
                title = item.find('title').text
                clean_title = title.split(" - ")[0]
                source_name = title.split(" - ")[-1] if " - " in title else "Google News"
                google_articles.append({'title': clean_title, 'url': item.find('link').text, 'source': {'name': source_name}})
                if len(google_articles) >= 15: break
    except: pass
    return google_articles

def start_process():
    search_query = " OR ".join([f'"{b}"' for b in MEINE_THEMEN[:20]])
    api_results = fetch_news_api(search_query)
    google_results = fetch_google_news(search_query)
    
    # --- INTERLEAVING LOGIK (Mixen) ---
    combined = []
    api_idx = 0
    google_idx = 0
    
    # Solange wir Material aus beiden Quellen haben
    while api_idx < len(api_results) or google_idx < len(google_results):
        # 2 Meldungen aus News-API
        for _ in range(2):
            if api_idx < len(api_results):
                combined.append(api_results[api_idx])
                api_idx += 1
        # 1 Meldung aus Google News
        if google_idx < len(google_results):
            combined.append(google_results[google_idx])
            google_idx += 1

    if not combined:
        combined = fetch_google_news("Videopodcast")
        status_text = "Backup-Modus"
    else:
        status_text = "Personalisiert"

    # KI Zusammenfassung
    headlines_for_ai = " \n".join([a['title'] for a in combined[:8]])
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Fasse kurz in MAXIMAL 12 Wörtern zusammen:\n\n{headlines_for_ai}"}]}]}
    
    summary = "Aktuelle Updates aus der Medienwelt."
    try:
        res = requests.post(gemini_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
        summary = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except: pass

    ticker_data = [{"title": summary, "is_ai": True}]
    for a in combined[:20]: # Zeige bis zu 20 gemischte Einträge
        source = a.get('source', {}).get('name', 'News')
        ticker_data.append({"title": a['title'], "url": a.get('url', '#'), "source": source})
    
    return ticker_data, status_text

ticker_entries, search_status = start_process()
now_ts = datetime.now().timestamp() * 1000 

# --- HTML (Design bleibt 1:1 erhalten) ---
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ margin: 0; padding: 0; background: transparent; font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; height: 85px; }}
        #podcast-news-widget {{ width: 100%; border: 1px solid rgb(255, 236, 192); border-radius: 0px; background: rgb(0, 21, 56); overflow: hidden; box-shadow: 0 3px 10px rgba(0,0,0,0.3); height: 85px; box-sizing: border-box; }}
        .ticker-header {{ background: rgb(255, 236, 192); color: rgb(0, 21, 56); padding: 5px 12px; font-weight: bold; font-size: 13px; display: flex; align-items: center; height: 24px; position: relative; overflow: hidden; }}
        #header-text-container {{ position: relative; height: 100%; width: 100%; display: flex; align-items: center; }}
        .header-msg {{ position: absolute; width: 100%; transition: all 0.6s ease; opacity: 0; transform: translateY(10px); }}
        .header-msg.active {{ opacity: 1; transform: translateY(0); }}
        .live-dot {{ height: 6px; width: 6px; background-color: #ff0000; border-radius: 50%; margin-right: 8px; flex-shrink: 0; animation: pulse 2s infinite ease-in-out; }}
        #progress-bar-container {{ width: 100%; height: 3px; background: rgba(0,0,0,0.2); }}
        #progress-bar {{ width: 0%; height: 100%; background: linear-gradient(to bottom, rgb(204, 189, 154) 0%, rgb(255, 236, 192) 100%); }}
        #feed-box {{ padding: 4px 12px; height: 38px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
        .status-tag {{ color: rgb(255, 236, 192); opacity: 0.5; font-size: 9px; text-transform: uppercase; margin-bottom: 2px; }}
        .news-text {{ color: rgb(255, 236, 192); font-size: 13px; line-height: 1.2; margin: 0; text-decoration: none; font-weight: bold; animation: fadeIn 0.5s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%; display: block; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(2px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes progress {{ from {{ width: 0%; }} to {{ width: 100%; }} }}
        @media (max-width: 768px) {{ .news-text {{ font-size: 15px; }} .ticker-header {{ font-size: 15px; height: 26px; }} .header-msg {{ font-size: 15px; }} .status-tag {{ font-size: 10px; }} }}
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
        const h1 = document.getElementById('h1');
        const h2 = document.getElementById('h2');
        setInterval(() => {{
            if(h1.classList.contains('active')) {{ h1.classList.remove('active'); h2.classList.add('active'); }}
            else {{ h2.classList.remove('active'); h1.classList.add('active'); }}
        }}, 4000);
        function getTimeAgo() {{
            const diff = Math.floor((Date.now() - updateTime) / 60000);
            if (diff < 1) return "Gerade eben";
            return `Vor ${{diff}} Min.`;
        }}
        function showNext() {{
            const entry = entries[currentIndex];
            bar.style.animation = 'none'; bar.offsetHeight; 
            bar.style.animation = 'progress 3.5s linear forwards';
            const timeLabel = getTimeAgo();
            status.innerText = entry.is_ai ? `KI-Fokus | ${{timeLabel}}` : `${{entry.source}} | ${{timeLabel}}`;
            box.innerHTML = entry.url !== "#" ? `<a href="${{entry.url}}" target="_blank" class="news-text">${{entry.title}}</a>` : `<p class="news-text">${{entry.title}}</p>`;
            currentIndex = (currentIndex + 1) % entries.length;
        }}
        setInterval(showNext, 3500);
        showNext();
    </script>
</body>
</html>
