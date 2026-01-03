import requests
import os
import json
from datetime import datetime

NEWS_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- DEINE OPTIMIERTE SUCHLISTE ---
SUCH_BEGRIFFE = [
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
    "Videopodcast", "Videopodcasts", "Talk Now", "TalkNow", "Talk?Now!"
]

# Suchanfrage erstellen
SUCH_QUERY = " OR ".join([f'"{b}"' for b in SUCH_BEGRIFFE])

def start_process():
    # Wir suchen global (ohne language=de), um alles zu finden
    news_url = f"https://newsapi.org/v2/everything?q={SUCH_QUERY}&sortBy=publishedAt&pageSize=15&apiKey={NEWS_KEY}"
    
    try:
        r = requests.get(news_url)
        news_data = r.json()
        articles = news_data.get('articles', [])
        
        if not articles:
            # Falls mit Anführungszeichen nichts gefunden wird, suchen wir etwas lockerer
            lockere_suche = " OR ".join(SUCH_BEGRIFFE[:10]) # Top 10 Begriffe locker
            news_url = f"https://newsapi.org/v2/everything?q={lockere_suche}&sortBy=publishedAt&pageSize=5&apiKey={NEWS_KEY}"
            r = requests.get(news_url)
            articles = r.json().get('articles', [])

        if not articles:
            return "Aktuell keine neuen Schlagzeilen zu den Shows oder Personen gefunden."

        # Schlagzeilen für die KI aufbereiten
        headlines = [f"{a['title']} ({a['source']['name']})" for a in articles]
        text_to_summarize = " \n".join(headlines)

        # Gemini 1.5 Flash für die Zusammenfassung
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": f"Du bist ein Medien-Experte. Fasse diese News zu Podcasts und Medien-Persönlichkeiten in 4 Sätzen auf Deutsch zusammen:\n\n{text_to_summarize}"}]}]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(gemini_url, json=payload, headers=headers)
        res_json = response.json()

        if "candidates" in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # Fallback: Liste mit Links
            html = "<b>Aktuelle Fundstücke:</b><br><br>"
            for a in articles[:8]:
                html += f"• <a href='{a['url']}' target='_blank' style='color: #e91e63; text-decoration: none; font-weight: 500;'>{a['title']}</a><br><br>"
            return html

    except Exception as e:
        return f"Dienst kurzzeitig im Standby."

# HTML Layout
result_text = start_process()
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; background-color: #f4f7f9; padding: 20px; display: flex; justify-content: center; }}
        .card {{ background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 25px rgba(0,0,0,0.06); max-width: 600px; width: 100%; border-left: 6px solid #e91e63; }}
        h1 {{ color: #333; font-size: 1.3rem; margin-top: 0; text-transform: uppercase; letter-spacing: 0.5px; }}
        .content {{ line-height: 1.8; color: #444; font-size: 1.05rem; white-space: pre-wrap; }}
        .date {{ font-size: 0.75rem; color: #999; margin-top: 30px; text-align: center; border-top: 1px solid #eee; padding-top: 15px; }}
        a {{ color: #e91e63; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Show & People Tracker</h1>
        <div class="content">{result_text}</div>
        <div class="date">Update: {datetime.now().strftime('%d.%m.%Y um %H:%M')} Uhr</div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
