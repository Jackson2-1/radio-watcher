import os
import requests

# Konfiguration (wird später über GitHub Secrets gesetzt)
# Falls lokal getestet wird, Fallback nutzen
WATCH = ["time of my life", "down under", "narcotic"]
URL = "https://api.nrjnet.de/webradio/nrj-nostalgie-de/current/nostalgie.json"
TOPIC = os.environ.get("NTFY_TOPIC", "phil_radio_alert") 

def fetch_titles():
    try:
        # Kein Timestamp nötig, da Server immer neu startet
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        titles = []
        if isinstance(data, list):
            for entry in data:
                artist = entry.get('artist') or entry.get('interpret') or "Unknown"
                title = entry.get('title') or entry.get('song') or "Unknown"
                titles.append(f"{artist} - {title}".lower())
        elif isinstance(data, dict):
            artist = data.get('artist') or data.get('interpret') or "Unknown"
            title = data.get('title') or data.get('song') or "Unknown"
            titles.append(f"{artist} - {title}".lower())
        return titles
    except Exception as e:
        print(f"⚠️ Fehler API: {e}")
        return []

def send_push(song_name):
    try:
        requests.post(
            f"https://ntfy.sh/{TOPIC}",
            data=f"🎵 Läuft jetzt: {song_name.upper()}".encode("utf-8"),
            headers={
                "Title": "Song Alarm",
                "Priority": "high",
                "Tags": "radio,music"
            }
        )
        print(f"✅ Push gesendet für: {song_name}")
    except Exception as e:
        print(f"❌ Push fehlgeschlagen: {e}")

def main():
    print("🚀 GitHub Action Check gestartet...")
    titles = fetch_titles()
    
    if not titles:
        print("Keine Daten.")
        return

    current_song = titles[0]
    print(f"Aktueller Song: {current_song}")

    for keyword in WATCH:
        if keyword in current_song:
            print(f"Treffer! '{keyword}' gefunden in '{current_song}'")
            send_push(current_song)
            # Wir beenden hier, damit wir nicht spammen, falls mehrere Keywords passen
            break 
        else:
            print(f"Kein Treffer für '{keyword}'")

if __name__ == "__main__":
    main()