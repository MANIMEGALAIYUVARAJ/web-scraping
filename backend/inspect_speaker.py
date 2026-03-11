import requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
url = "https://europe.money2020.com/agenda/speakers/maya-atig-s102-106509"
try:
    r = requests.get(url, headers=headers)
    with open("c:/Users/MANIMEGALAI/Desktop/AIOne_Scrapper-main/backend/speaker_detail_debug.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("Saved speaker_detail_debug.html")
except Exception as e:
    print(f"Error: {e}")
